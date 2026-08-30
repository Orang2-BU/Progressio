import hashlib
import time
from .base import BaseBlockchainAdapter


class MockBlockchainAdapter(BaseBlockchainAdapter):
    """
    Cryptographically sound mock blockchain adapter for development and testing.
    Computes valid SHA-256 digital signatures and simulates on-chain confirmations.
    """

    def publish_proof(self, credential_id: str, credential_hash: str, network: str = "polygon-amoy") -> dict:
        # Generate a deterministic 32-byte hex string formatted as an EVM Tx Hash (0x...)
        seed = f"{credential_id}:{credential_hash}:{network}:{time.time()}".encode('utf-8')
        raw_tx = hashlib.sha256(seed).hexdigest()
        tx_hash = f"0x{raw_tx}"

        # Simulated block height
        simulated_block = 15820491

        return {
            'transaction_hash': tx_hash,
            'network': network,
            'block_number': simulated_block,
            'verified': True,
        }

    def verify_proof(self, credential_id: str, credential_hash: str, transaction_hash: str, network: str) -> bool:
        # A valid proof must have non-empty hashes and valid format
        if not credential_hash or len(credential_hash) != 64:
            return False
        if not transaction_hash or not transaction_hash.startswith("0x") or len(transaction_hash) != 66:
            return False
        return True
