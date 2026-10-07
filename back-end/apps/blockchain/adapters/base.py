from abc import ABC, abstractmethod


class BaseBlockchainAdapter(ABC):
    """Abstract interface for Blockchain Network adapters."""

    supports_recovery = False

    def lookup_proof(self, idempotency_key: str):
        """Return the original receipt, or None for authoritative absence; errors are unknown."""
        raise NotImplementedError('Provider has no recovery contract.')

    @abstractmethod
    def publish_proof(self, credential_id: str, credential_hash: str, network: str = "polygon-amoy", idempotency_key: str = '') -> dict:
        """
        Publishes the SHA-256 hash proof to the target blockchain.
        Returns dict containing transaction_hash, network, block_number, verified.
        """
        pass

    @abstractmethod
    def verify_proof(self, credential_id: str, credential_hash: str, transaction_hash: str, network: str) -> bool:
        """
        Validates on-chain hash integrity against the local hash.
        """
        pass
