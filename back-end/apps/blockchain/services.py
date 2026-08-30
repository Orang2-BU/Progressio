import hashlib
import json
import os
from .models import BlockchainCredential
from .adapters.mock import MockBlockchainAdapter


class BlockchainService:
    """
    Service Layer for Cryptographic Hashing and Blockchain Proof Management.
    Enforces privacy by design: Only SHA-256 hashes are anchored on-chain.
    """

    @classmethod
    def get_adapter(cls):
        # Extendable for Web3 live adapter via BLOCKCHAIN_PROVIDER env
        return MockBlockchainAdapter()

    @classmethod
    def compute_credential_hash(cls, credential):
        """
        Creates a canonical deterministic JSON snapshot of the credential
        and produces its SHA-256 cryptographic digest.
        """
        canonical_data = {
            'credential_id': str(credential.id),
            'competency_title': credential.competency.title,
            'career_track': credential.competency.career_track.title if credential.competency.career_track else '',
            'student_username': credential.user.username,
            'score': round(float(credential.score), 2),
            'issued_at': credential.issued_at.isoformat() if credential.issued_at else '',
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
        is_intact = (current_hash == proof.credential_hash) and proof.verified and not proof.revoked
        return is_intact, current_hash, proof
