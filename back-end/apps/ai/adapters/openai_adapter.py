"""Legacy alias — dipertahankan agar kode lama tidak rusak.

Jangan pakai untuk kode baru; pakai `HttpAIAdapter` (apps.ai.adapters.http_adapter)
dengan AI_PROVIDER=http + AI_API_URL. Variabel OPENAI_* lama tetap dibaca
sebagai fallback agar deployment lama tidak langsung error.
"""
import os

from .http_adapter import AIProviderError, HttpAIAdapter  # noqa: F401


class OpenAIAdapter(HttpAIAdapter):
    """Deprecated: thin wrapper di atas HttpAIAdapter."""

    def __init__(self, api_key=None, model=None, timeout=None, allow_mock_fallback=None,
                 api_url=None, base_url=None):
        url = (
            api_url
            or os.getenv('AI_API_URL', '').strip()
            or (os.getenv('OPENAI_BASE_URL', '').rstrip('/') + '/responses'
                if os.getenv('OPENAI_BASE_URL', '').strip() else '')
        )
        super().__init__(
            api_url=url,
            api_key=api_key or os.getenv('AI_API_KEY', '') or os.getenv('OPENAI_API_KEY', ''),
            model=model or os.getenv('AI_MODEL', '') or os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'),
            timeout=timeout or os.getenv('AI_TIMEOUT_SECONDS', '') or os.getenv('OPENAI_TIMEOUT_SECONDS', '45'),
            allow_mock_fallback=allow_mock_fallback,
        )
