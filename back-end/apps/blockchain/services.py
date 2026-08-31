import hashlib
import json
import logging
import os
from .models import BlockchainCredential
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
            'competency_id': credential.competency.slug,
            'competency_title': metadata.get('competency_title', credential.competency.title),
            'career_track': metadata.get(
                'career_track_title',
                track.title if track else '',
            ),
            'career_track_id': track.slug if track else '',
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
            'issued_at': credential.issued_at.isoformat() if credential.issued_at else '',
            'evidence': evidence,
        }
        canonical_json = json.dumps(canonical_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

    @classmethod
    def record_credential_on_chain(cls, credential, network=None):
        """
        Calculates SHA-256 digest and records the immutable proof on the blockchain.
        """
        if not network:
            network = os.getenv('BLOCKCHAIN_NETWORK', 'polygon-amoy')

        credential_hash = cls.compute_credential_hash(credential)
        adapter = cls.get_adapter()
        proof = adapter.publish_proof(
            credential_id=str(credential.id),
            credential_hash=credential_hash,
            network=network
        )
        if not proof.get('transaction_hash') or proof.get('verified') is not True:
            raise ValueError('Blockchain provider did not return a confirmed transaction proof.')

        bc_credential, _ = BlockchainCredential.objects.update_or_create(
            credential=credential,
            defaults={
                'credential_hash': credential_hash,
                'transaction_hash': proof['transaction_hash'],
                'network': proof['network'],
                'block_number': proof.get('block_number'),
                'verified': proof.get('verified', True),
                'revoked': False,
            }
        )
        return bc_credential

    @classmethod
    def verify_credential_integrity(cls, credential):
        """
        Recomputes hash and validates against registered blockchain proof.
        Returns (is_intact, current_hash, registered_proof).
        """
        proof = getattr(credential, 'blockchain_proof', None)
        if not proof:
            return False, None, None

        current_hash = cls.compute_credential_hash(credential)
        adapter = cls.get_adapter()
        try:
            provider_verified = adapter.verify_proof(
                credential_id=str(credential.id),
                credential_hash=proof.credential_hash,
                transaction_hash=proof.transaction_hash,
                network=proof.network,
            )
        except Exception:
            logger.exception('Credential proof verification failed for %s.', credential.id)
            provider_verified = False
        is_intact = (
            current_hash == proof.credential_hash
            and proof.verified
            and not proof.revoked
            and provider_verified
        )
        return is_intact, current_hash, proof
