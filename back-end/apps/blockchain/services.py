import hashlib
import json
import logging
import os
import re
from datetime import timedelta
from django.db import connection, transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from apps.credentials.models import Credential
from .models import BlockchainCredential, ProofDelivery, ProofAttempt
from .adapters.mock import MockBlockchainAdapter
from .adapters.http import HTTPBlockchainAdapter


logger = logging.getLogger(__name__)


class BlockchainService:
    """
    Service Layer for Cryptographic Hashing and Blockchain Proof Management.
    Enforces privacy by design: Only SHA-256 hashes are anchored on-chain.
    """

    @classmethod
    def get_adapter(cls):
        provider = os.getenv('BLOCKCHAIN_PROVIDER', 'mock').lower()
        if provider == 'mock':
            return MockBlockchainAdapter()
        if provider == 'http':
            return HTTPBlockchainAdapter()
        raise ValueError(f"Unsupported BLOCKCHAIN_PROVIDER '{provider}'.")

    @classmethod
    def compute_credential_hash(cls, credential):
        """
        Creates a canonical deterministic JSON snapshot of the credential
        and produces its SHA-256 cryptographic digest.
        """
        metadata = credential.metadata if isinstance(credential.metadata, dict) else {}
        evidence = [
            {
                'submission_id': item.submission_id,
                'github_url': item.github_url,
                'file_url': item.file_url,
                'demo_url': item.demo_url,
                'notes': item.notes,
            }
            for item in credential.evidences.order_by('id')
        ]
        track = credential.competency.career_track
        canonical_data = {
            'credential_id': str(credential.id),
            # Slugs, not titles: a title may be reworded without changing what
            # was actually assessed.
            'competency_id': metadata.get('competency_id', credential.competency.slug),
            'competency_title': metadata.get('competency_title', credential.competency.title),
            'career_track': metadata.get(
                'career_track_title',
                track.title if track else '',
            ),
            'career_track_id': metadata.get('career_track_id', track.slug if track else ''),
            # Which version of the standard graded this claim. Without it, two
            # credentials reading "API Development - 85" can mean different
            # things once the curriculum changes.
            'curriculum_version': metadata.get(
                'curriculum_version', track.curriculum_version if track else ''
            ),
            'curriculum_schema_version': metadata.get(
                'curriculum_schema_version',
                track.curriculum_schema_version if track else 0,
            ),
            'student_name': metadata.get(
                'student_name', credential.user.get_full_name() or credential.user.username
            ),
            'score': round(float(credential.score), 2),
            # Reserve the timestamp in the snapshot; only confirmed credentials expose issued_at.
            'issued_at': credential.issued_at.isoformat() if credential.issued_at else metadata.get('issued_at') or '',
            'evidence': evidence,
        }
        if 'skill_standards' in metadata:
            canonical_data['standard'] = {key: metadata.get(key) for key in ('skill_standards', 'observable_behaviors', 'mode', 'proof_provider', 'submission_ids')}
        canonical_json = json.dumps(canonical_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

    @classmethod
    def provider_identity(cls):
        provider = os.getenv('BLOCKCHAIN_PROVIDER', 'mock').lower()
        endpoint = os.getenv('BLOCKCHAIN_SERVICE_URL', '').rstrip('/') if provider == 'http' else ''
        return provider, hashlib.sha256(endpoint.encode()).hexdigest()

    @classmethod
    def prepare_delivery(cls, credential, network=None):
        provider, endpoint_hash = cls.provider_identity()
        delivery, _ = ProofDelivery.objects.get_or_create(credential=credential, defaults={
            'credential_hash': cls.compute_credential_hash(credential),
            'network': network or os.getenv('BLOCKCHAIN_NETWORK', 'polygon-amoy'),
            'provider': provider, 'endpoint_hash': endpoint_hash,
        })
        return delivery

    @classmethod
    def record_credential_on_chain(cls, credential, network=None):
        """Claim a committed delivery, perform I/O without DB locks, reconcile unknown outcomes."""
        if connection.in_atomic_block:
            raise RuntimeError('Proof delivery cannot run inside an outer database transaction.')
        with transaction.atomic():
            current = Credential.objects.select_for_update().get(pk=credential.pk)
            if current.status in (Credential.Status.DRAFT, Credential.Status.REVOKED) or current.metadata.get('mode') == 'demo':
                return None
            delivery = cls.prepare_delivery(current, network)
            if delivery.state == ProofDelivery.State.CONFIRMED:
                return BlockchainCredential.objects.filter(credential=current).first()
            if delivery.state == ProofDelivery.State.FAILED and delivery.error_code != 'contract_blocked':
                return None
            if delivery.lease_until and delivery.lease_until > timezone.now():
                return None
            previous_state = delivery.state
            # Expired claims are still uncertain, even if the process died before POST.
            ProofAttempt.objects.filter(delivery=delivery, outcome='started').update(outcome='unknown', error_code='lease_expired')
            attempt = ProofAttempt.objects.create(delivery=delivery,
                operation='publish' if previous_state in (ProofDelivery.State.READY, ProofDelivery.State.FAILED) else 'reconcile')
            delivery.active_attempt = attempt.pk
            delivery.state = ProofDelivery.State.SENDING
            delivery.lease_until = timezone.now() + timedelta(seconds=max(300, int(os.getenv('BLOCKCHAIN_TIMEOUT_SECONDS', '30')) * 2 + 60))
            delivery.error_code = ''
            delivery.save()

        if cls.provider_identity() != (delivery.provider, delivery.endpoint_hash) or (network and network != delivery.network):
            cls._finish_attempt(delivery, attempt, error_code='provider_changed', failed=True)
            return None
        if cls.compute_credential_hash(current) != delivery.credential_hash:
            cls._finish_attempt(delivery, attempt, error_code='hash_mismatch', failed=True)
            return None
        try:
            adapter = cls.get_adapter()
            if not adapter.supports_recovery:
                cls._finish_attempt(delivery, attempt, error_code='contract_blocked', failed=True)
                return None
            receipt = adapter.lookup_proof(str(delivery.idempotency_key)) if attempt.operation == 'reconcile' else None
            if receipt is None:
                receipt = adapter.publish_proof(credential_id=str(current.pk),
                    credential_hash=delivery.credential_hash, network=delivery.network,
                    idempotency_key=str(delivery.idempotency_key))
            if not cls._receipt_matches(delivery, receipt):
                cls._finish_attempt(delivery, attempt, error_code='receipt_mismatch', failed=True)
                return None
            if receipt.get('verified') is not True:
                cls._finish_attempt(delivery, attempt, error_code='unconfirmed')
                return None
            if adapter.verify_proof(str(current.pk), delivery.credential_hash, receipt['transaction_hash'], delivery.network) is not True:
                cls._finish_attempt(delivery, attempt, error_code='unconfirmed')
                return None
        except Exception:
            # A timeout or malformed response says nothing about external acceptance.
            # Never persist exception text, raw response bodies, tokens or evidence.
            cls._finish_attempt(delivery, attempt, error_code='provider_error')
            return None
        # Deliberately outside the provider error handler: a DB crash leaves a durable in-flight claim.
        return cls._finish_attempt(delivery, attempt, receipt=receipt)

    @classmethod
    def _receipt_matches(cls, delivery, receipt):
        return (isinstance(receipt, dict)
            and receipt.get('credential_id') == str(delivery.credential_id)
            and receipt.get('credential_hash') == delivery.credential_hash
            and receipt.get('network') == delivery.network
            and isinstance(receipt.get('transaction_hash'), str)
            and re.fullmatch(r'0x[0-9a-fA-F]{64}', receipt['transaction_hash']) is not None
            and (receipt.get('block_number') is None or (type(receipt['block_number']) is int and 0 <= receipt['block_number'] <= 2147483647)))

    @classmethod
    def _finish_attempt(cls, delivery, attempt, receipt=None, error_code='', failed=False):
        with transaction.atomic():
            current = Credential.objects.select_for_update().get(pk=delivery.credential_id)
            saved = ProofDelivery.objects.select_for_update().get(pk=delivery.pk)
            if saved.active_attempt != attempt.pk:
                ProofAttempt.objects.filter(pk=attempt.pk).update(outcome='superseded')
                return None
            if current.status == Credential.Status.REVOKED:
                error_code, failed = 'revoked', True
            elif cls.compute_credential_hash(current) != saved.credential_hash:
                error_code, failed = 'hash_mismatch', True
            proof = None
            if receipt is not None and not error_code:
                proof, _ = BlockchainCredential.objects.get_or_create(credential=current, defaults={
                    'credential_hash': saved.credential_hash, 'transaction_hash': receipt['transaction_hash'],
                    'network': saved.network, 'block_number': receipt.get('block_number'), 'verified': True,
                })
                if proof.revoked or proof.credential_hash != saved.credential_hash or proof.transaction_hash != receipt['transaction_hash'] or proof.network != saved.network or not proof.verified:
                    error_code, failed, proof = 'proof_conflict', True, None
            if proof:
                saved.state = ProofDelivery.State.CONFIRMED
                current.status = Credential.Status.ISSUED
                if current.issued_at is None:
                    current.issued_at = parse_datetime(current.metadata['issued_at']) if current.metadata.get('issued_at') else None
            else:
                saved.state = ProofDelivery.State.FAILED if failed else ProofDelivery.State.UNKNOWN
                if current.status != Credential.Status.REVOKED:
                    current.status = Credential.Status.FAILED if failed else Credential.Status.PENDING
            saved.error_code = error_code
            saved.lease_until = None
            saved.active_attempt = None
            saved.save()
            current.save(update_fields=['status', 'issued_at', 'updated_at'])
            ProofAttempt.objects.filter(pk=attempt.pk).update(outcome='confirmed' if proof else 'failed' if failed else 'unknown',
                error_code=error_code, transaction_hash=receipt['transaction_hash'] if receipt is not None else '')
            return proof

    @classmethod
    def verify_credential_integrity(cls, credential):
        """
        Recomputes hash and validates against registered blockchain proof.
        Returns (is_intact, current_hash, registered_proof).
        """
        proof = getattr(credential, 'blockchain_proof', None)
        if credential.status != Credential.Status.ISSUED:
            return False, None, proof
        if not proof:
            return False, None, None

        current_hash = cls.compute_credential_hash(credential)
        try:
            adapter = cls.get_adapter()
            provider_verified = adapter.verify_proof(
                credential_id=str(credential.id),
                credential_hash=proof.credential_hash,
                transaction_hash=proof.transaction_hash,
                network=proof.network,
            )
        except Exception:
            logger.warning('Credential proof verification failed for %s.', credential.id)
            provider_verified = False
        is_intact = (
            current_hash == proof.credential_hash
            and proof.verified
            and not proof.revoked
            and provider_verified
        )
        return is_intact, current_hash, proof
