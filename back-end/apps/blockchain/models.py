import uuid
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


class ProofDelivery(TimestampMixin):
    """Durable outbox: immutable identity and digest, never evidence or provider secrets."""

    class State(models.TextChoices):
        READY = 'ready', 'Ready'
        SENDING = 'sending', 'In flight'
        UNKNOWN = 'unknown', 'Outcome unknown'
        CONFIRMED = 'confirmed', 'Confirmed'
        FAILED = 'failed', 'Blocked or rejected'

    credential = models.OneToOneField(Credential, on_delete=models.CASCADE, related_name='proof_delivery')
    idempotency_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    credential_hash = models.CharField(max_length=64)
    network = models.CharField(max_length=50)
    provider = models.CharField(max_length=20)
    endpoint_hash = models.CharField(max_length=64)
    state = models.CharField(max_length=20, choices=State.choices, default=State.READY)
    active_attempt = models.UUIDField(null=True)
    lease_until = models.DateTimeField(null=True)
    error_code = models.CharField(max_length=40, blank=True)


class ProofAttempt(TimestampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delivery = models.ForeignKey(ProofDelivery, on_delete=models.CASCADE, related_name='attempts')
    operation = models.CharField(max_length=20)  # publish or reconcile (lookup, then safe replay)
    outcome = models.CharField(max_length=20, default='started')
    error_code = models.CharField(max_length=40, blank=True)
    transaction_hash = models.CharField(max_length=66, blank=True)
