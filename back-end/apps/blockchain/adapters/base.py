from abc import ABC, abstractmethod


class BaseBlockchainAdapter(ABC):
    """
    Abstract interface for Blockchain Network adapters (Clean Architecture).
    """

    @abstractmethod
    def publish_proof(self, credential_id: str, credential_hash: str, network: str = "polygon-amoy") -> dict:
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
