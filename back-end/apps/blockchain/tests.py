from django.test import TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from eth_account import Account
from eth_utils import keccak

from apps.careers.models import CareerTrack
from apps.competencies.models import Competency
from apps.credentials.models import Credential
from .models import BlockchainCredential, DemoAnchor
from .services import BlockchainService
from .tasks import publish_credential_to_blockchain_task
from .demo_anchor import DemoAnchorError, process_demo_anchor, queue_demo_anchor

User = get_user_model()


class BlockchainServiceAndAPITests(TransactionTestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='chain_student', email='chain@example.com', password='Password123!', role='student'
        )
        self.track = CareerTrack.objects.create(title='Full Stack', slug='full-stack')
        self.comp = Competency.objects.create(
            career_track=self.track, title='System Architecture', slug='system-architecture', order=1
        )
        self.credential = Credential.objects.create(
            user=self.user,
            competency=self.comp,
            status=Credential.Status.ISSUED,
            score=92.0,
            metadata={'student_name': 'Chain Student'}
        )

    def test_compute_hash_deterministic(self):
        """SHA-256 hash must be exactly 64 hex characters and deterministic."""
        hash1 = BlockchainService.compute_credential_hash(self.credential)
        hash2 = BlockchainService.compute_credential_hash(self.credential)
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)

    def test_record_and_verify_on_chain(self):
        """Proof recording should generate transaction hash and verify integrity."""
        proof = BlockchainService.record_credential_on_chain(self.credential, network='polygon-amoy')
        self.assertEqual(proof.network, 'polygon-amoy')
        self.assertTrue(proof.transaction_hash.startswith('0x'))
        self.assertEqual(len(proof.transaction_hash), 66)
        self.assertTrue(proof.verified)

        is_intact, current_hash, reg_proof = BlockchainService.verify_credential_integrity(self.credential)
        self.assertTrue(is_intact)
        self.assertEqual(current_hash, proof.credential_hash)

        self.credential.score = 99.0
        self.credential.save(update_fields=['score'])
        is_intact, _, _ = BlockchainService.verify_credential_integrity(self.credential)
        self.assertFalse(is_intact)

    def test_blockchain_proof_endpoint(self):
        """Public endpoint should return proof details."""
        BlockchainService.record_credential_on_chain(self.credential, network='polygon-amoy')

        url = reverse('blockchain-proof-detail', args=[self.credential.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['network'], 'polygon-amoy')
        self.assertTrue(response.data['verified'])
        self.assertTrue(response.data['transaction_hash'].startswith('0x'))

    def test_publish_credential_celery_task(self):
        """Celery task should execute and record proof in DB."""
        result = publish_credential_to_blockchain_task(self.credential.id)
        self.assertIn("successfully anchored on Blockchain", result)

        self.assertTrue(BlockchainCredential.objects.filter(credential=self.credential).exists())

    def _demo_credential(self):
        credential = Credential.objects.create(user=self.user, competency=self.comp,
            status=Credential.Status.DRAFT, score=92.0, metadata={'mode': 'demo', 'student_name': 'Chain Student'})
        return credential

    def test_demo_anchor_queue_keeps_credential_draft(self):
        credential = self._demo_credential()
        account = Account.from_key('0x' + '11' * 32)
        with patch.dict('os.environ', {'DEMO_ANCHOR_SIGNER_ADDRESS': account.address}):
            anchor = queue_demo_anchor(credential)
        credential.refresh_from_db()
        self.assertEqual(anchor.state, DemoAnchor.State.QUEUED)
        self.assertEqual(anchor.network, 'base-sepolia')
        self.assertEqual(anchor.chain_id, 84532)
        self.assertEqual(credential.status, Credential.Status.DRAFT)
        self.assertFalse(hasattr(anchor, 'private_key'))

    def test_demo_anchor_requires_draft_demo_and_configured_signer(self):
        with patch.dict('os.environ', {}, clear=False):
            import os
            os.environ.pop('DEMO_ANCHOR_SIGNER_ADDRESS', None)
            with self.assertRaises(DemoAnchorError):
                queue_demo_anchor(self.credential)

    def test_demo_anchor_worker_persists_replayable_signed_transaction(self):
        credential = self._demo_credential()
        account = Account.from_key('0x' + '12' * 32)
        with patch.dict('os.environ', {'DEMO_ANCHOR_SIGNER_ADDRESS': account.address}):
            anchor = queue_demo_anchor(credential)

        class RPC:
            def __init__(self): self.calls = []
            def call(self, method, params):
                self.calls.append(method)
                if method == 'eth_sendRawTransaction':
                    return '0x' + keccak(bytes.fromhex(params[0][2:])).hex()
                return {'eth_chainId': '0x14a34', 'eth_getTransactionCount': '0x0',
                    'eth_gasPrice': '0x3b9aca00', 'eth_getTransactionReceipt': None}.get(method)

        rpc = RPC()
        with patch.dict('os.environ', {'DEMO_ANCHOR_PRIVATE_KEY': '0x' + '12' * 32}):
            result = process_demo_anchor(anchor.pk, rpc=rpc)
        self.assertEqual(result.state, DemoAnchor.State.SUBMITTED)
        self.assertTrue(result.raw_signed_transaction.startswith('0x'))
        self.assertEqual(result.credential.status, Credential.Status.DRAFT)

    def test_demo_anchor_confirms_only_matching_calldata_after_two_blocks(self):
        credential = self._demo_credential()
        account = Account.from_key('0x' + '14' * 32)
        with patch.dict('os.environ', {'DEMO_ANCHOR_SIGNER_ADDRESS': account.address}):
            anchor = queue_demo_anchor(credential)

        class RPC:
            def call(self, method, params):
                if method == 'eth_sendRawTransaction':
                    return '0x' + keccak(bytes.fromhex(params[0][2:])).hex()
                return {'eth_chainId': '0x14a34', 'eth_getTransactionCount': '0x0',
                    'eth_gasPrice': '0x3b9aca00',
                    'eth_getTransactionReceipt': {'status': '0x1', 'blockNumber': '0xa'},
                    'eth_getTransactionByHash': {'from': account.address, 'to': account.address,
                        'input': '0x' + anchor.credential_hash}, 'eth_blockNumber': '0xb'}[method]

        with patch.dict('os.environ', {'DEMO_ANCHOR_PRIVATE_KEY': '0x' + '14' * 32}):
            result = process_demo_anchor(anchor.pk, rpc=RPC())
        credential.refresh_from_db()
        self.assertEqual(result.state, DemoAnchor.State.CONFIRMED)
        self.assertEqual(result.block_number, 10)
        self.assertEqual(credential.status, Credential.Status.DRAFT)

    def test_demo_anchor_endpoint_is_owner_scoped_and_never_returns_signed_tx(self):
        credential = self._demo_credential()
        account = Account.from_key('0x' + '13' * 32)
        other = User.objects.create_user(username='other_chain_student', password='Password123!', role='student')
        self.client.force_authenticate(other)
        url = reverse('demo-anchor-detail', args=[credential.pk])
        self.assertEqual(self.client.post(url).status_code, status.HTTP_404_NOT_FOUND)
        self.client.force_authenticate(self.user)
        with patch.dict('os.environ', {'DEMO_ANCHOR_SIGNER_ADDRESS': account.address}):
            response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertNotIn('raw_signed_transaction', response.data)
        self.assertNotIn('private_key', response.data)
