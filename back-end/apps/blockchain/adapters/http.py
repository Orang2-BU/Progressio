import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .base import BaseBlockchainAdapter


class BlockchainProviderError(RuntimeError):
    """Raised when the configured blockchain anchoring service fails."""


class HTTPBlockchainAdapter(BaseBlockchainAdapter):
    """Adapter for an external service that owns keys and submits chain transactions."""

    def __init__(self, service_url=None, api_token=None, timeout=None):
        self.service_url = (service_url or os.getenv('BLOCKCHAIN_SERVICE_URL', '')).rstrip('/')
        self.api_token = api_token or os.getenv('BLOCKCHAIN_SERVICE_TOKEN', '')
        self.timeout = timeout or int(os.getenv('BLOCKCHAIN_TIMEOUT_SECONDS', '30'))
        if not self.service_url:
            raise BlockchainProviderError(
                'BLOCKCHAIN_SERVICE_URL is required when BLOCKCHAIN_PROVIDER=http.'
            )

    def publish_proof(self, credential_id, credential_hash, network='polygon-amoy'):
        return self._post('/proofs', {
            'credential_id': credential_id,
            'credential_hash': credential_hash,
            'network': network,
        })

    def verify_proof(self, credential_id, credential_hash, transaction_hash, network):
        result = self._post('/proofs/verify', {
            'credential_id': credential_id,
            'credential_hash': credential_hash,
            'transaction_hash': transaction_hash,
            'network': network,
        })
        return result.get('verified') is True

    def _post(self, path, payload):
        headers = {'Content-Type': 'application/json'}
        if self.api_token:
            headers['Authorization'] = f'Bearer {self.api_token}'
        request = Request(
            f'{self.service_url}{path}',
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST',
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except HTTPError as exc:
            detail = exc.read().decode('utf-8', errors='replace')[:500]
            raise BlockchainProviderError(
                f'Blockchain service returned HTTP {exc.code}: {detail}'
            ) from exc
        except (URLError, TimeoutError, ValueError) as exc:
            raise BlockchainProviderError(f'Blockchain service request failed: {exc}') from exc
