from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.careers.models import CareerTrack
from apps.competencies.models import Competency
from apps.credentials.models import Credential
from .models import BlockchainCredential
from .services import BlockchainService
from .tasks import publish_credential_to_blockchain_task

User = get_user_model()


class BlockchainServiceAndAPITests(TestCase):

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
