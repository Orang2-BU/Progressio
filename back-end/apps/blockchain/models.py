from django.db import models
from apps.common.models import TimestampMixin
from apps.credentials.models import Credential


class BlockchainCredential(TimestampMixin):
    """
    Stores immutable cryptographic proof of a Credential on the Blockchain.
    Contains only hash proofs (NEVER student PII or raw exam data).
    """
    credential = models.OneToOneField(
        Credential,
        on_delete=models.CASCADE,
        related_name='blockchain_proof'
    )
    credential_hash = models.CharField(
        max_length=64,
        help_text="SHA-256 cryptographic hash of the canonical credential snapshot."
    )
    transaction_hash = models.CharField(
        max_length=66,
        help_text="Immutable transaction hash on the blockchain."
    )
    network = models.CharField(
        max_length=50,
        default='polygon-amoy',
        help_text="Blockchain network where proof is registered."
    )
    block_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Block height of the registered transaction."
    )
    verified = models.BooleanField(
        default=True,
        help_text="True if on-chain proof is confirmed valid."
    )
    revoked = models.BooleanField(
        default=False,
        help_text="True if credential has been marked revoked on-chain."
    )

    class Meta:
        db_table = 'blockchain_credentials'
        ordering = ['-created_at']
        verbose_name = 'Blockchain Credential'
        verbose_name_plural = 'Blockchain Credentials'

    def __str__(self):
        return f"Blockchain Proof [{self.credential_id}] - Tx: {self.transaction_hash[:10]}..."
