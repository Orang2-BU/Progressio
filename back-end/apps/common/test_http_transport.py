import unittest
import os
from unittest.mock import Mock, patch
from urllib.error import HTTPError
from urllib.request import Request

from apps.common.http_transport import (
    RedirectRejected,
    _NoRedirect,
    open_provider_request,
    validate_provider_url,
)
from apps.ai.adapters.http_adapter import AIProviderError, HttpAIAdapter
from apps.blockchain.adapters.http import BlockchainProviderError, HTTPBlockchainAdapter


class ProviderTransportTests(unittest.TestCase):
    def test_rejects_http_credentials_and_non_loopback_http(self):
        for url, has_credentials in (
            ('http://ai.example.test/v1', False),
            ('http://127.0.0.1/v1', True),
            ('https://user:password@ai.example.test/v1', True),
            ('https://ai.example.test/v1#fragment', False),
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_provider_url(url, has_credentials=has_credentials,
                                      allowed_hosts={'ai.example.test'})

    def test_allows_https_and_unauthenticated_loopback_http_only(self):
        self.assertEqual(validate_provider_url('https://ai.example.test/v1', has_credentials=True,
                                               allowed_hosts={'ai.example.test'}),
                         'https://ai.example.test/v1')
        with self.assertRaisesRegex(ValueError, 'trusted-host allowlist'):
            validate_provider_url('https://internal.example.test/v1', has_credentials=True,
                                  allowed_hosts={'ai.example.test'})
        self.assertEqual(validate_provider_url('http://[::1]:8080/v1', has_credentials=False),
                         'http://[::1]:8080/v1')

    def test_production_rejects_even_unauthenticated_loopback_http(self):
        with patch.dict(os.environ, {'APP_ENV': 'production'}):
            with self.assertRaisesRegex(ValueError, 'only in local development'):
                validate_provider_url('http://127.0.0.1:8080/v1', has_credentials=False)

    def test_provider_adapters_reject_insecure_urls_before_network(self):
        with self.assertRaises(ValueError):
            HttpAIAdapter(api_url='http://ai.example.test/v1', api_key='synthetic-key')
        with self.assertRaises(ValueError):
            HTTPBlockchainAdapter(service_url='http://signer.example.test', api_token='synthetic-token')
        HttpAIAdapter(api_url='http://127.0.0.1:8080/v1', api_key='')
        HTTPBlockchainAdapter(service_url='http://localhost:8080', api_token='')

    def test_provider_refusal_text_is_not_exposed_in_exceptions(self):
        adapter = HttpAIAdapter(api_url='https://ai.example.test/v1',
                                allowed_hosts={'ai.example.test'})
        with self.assertRaises(AIProviderError) as raised:
            adapter._extract_json({'output': [{'content': [
                {'type': 'refusal', 'refusal': 'synthetic sensitive provider response'}]}]})
        self.assertNotIn('synthetic sensitive provider response', str(raised.exception))

    def test_blockchain_redirect_is_not_followed_or_exposed(self):
        adapter = HTTPBlockchainAdapter(
            service_url='https://signer.example.test', api_token='synthetic-token',
            allowed_hosts={'signer.example.test'})
        redirect = HTTPError(
            'https://signer.example.test/proofs', 307, 'Temporary Redirect',
            {'Location': 'https://attacker.example.test/collect'}, None)
        with patch('apps.blockchain.adapters.http.open_provider_request', side_effect=redirect) as opened:
            with self.assertRaises(BlockchainProviderError) as raised:
                adapter._post('/proofs', {'credential_id': 'synthetic-id'})
        self.assertEqual(opened.call_count, 1)
        self.assertEqual(str(raised.exception), 'Blockchain service returned HTTP 307.')

    def test_redirect_handler_never_creates_a_followup_request(self):
        redirect = _NoRedirect().redirect_request(
            Request('https://ai.example.test/v1'), None, 302, 'Found', {},
            'https://attacker.example/collect')
        self.assertIsNone(redirect)

    def test_redirect_response_is_rejected_without_following(self):
        for code, target in ((301, 'https://attacker.example/'),
                             (302, 'http://ai.example.test/'),
                             (303, 'https://ai.example.test:8443/'),
                             (307, 'https://attacker.example/step-2')):
            opener = Mock()
            opener.open.side_effect = HTTPError(
                'https://ai.example.test/v1', code, 'Redirect', {'Location': target}, None)
            builder = Mock(return_value=opener)
            with self.subTest(code=code, target=target), \
                    patch('apps.common.http_transport.build_opener', builder):
                with self.assertRaises(RedirectRejected):
                    open_provider_request(Request('https://ai.example.test/v1'), timeout=2)
            self.assertIsInstance(builder.call_args.args[0], _NoRedirect)
            opener.open.assert_called_once()


if __name__ == '__main__':
    unittest.main()
