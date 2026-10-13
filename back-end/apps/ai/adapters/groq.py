"""Groq Chat Completions adapter with strict JSON Schema output."""
import json
import os

from django.core.exceptions import ImproperlyConfigured

from .http_adapter import AIProviderError, HttpAIAdapter


class GroqAIAdapter(HttpAIAdapter):
    provider_name = 'groq'
    API_URL = 'https://api.groq.com/openai/v1/chat/completions'
    DEFAULT_MODEL = 'openai/gpt-oss-20b'

    def __init__(self, api_key=None, model=None, timeout=None, api_url=None,
                 allow_mock_fallback=None):
        key = api_key if api_key is not None else os.getenv('GROQ_API_KEY', '')
        if not key.strip():
            raise ImproperlyConfigured('GROQ_API_KEY is required when AI_PROVIDER=groq.')
        self.max_completion_tokens = int(os.getenv('AI_MAX_COMPLETION_TOKENS', '2048'))
        if self.max_completion_tokens < 1 or self.max_completion_tokens > 8192:
            raise ImproperlyConfigured('AI_MAX_COMPLETION_TOKENS must be between 1 and 8192.')
        timeout_value = timeout or os.getenv('AI_TIMEOUT_SECONDS', '10')
        try:
            timeout_seconds = int(timeout_value)
        except (TypeError, ValueError) as exc:
            raise ImproperlyConfigured('AI_TIMEOUT_SECONDS must be an integer between 1 and 10.') from exc
        if timeout_seconds < 1 or timeout_seconds > 10:
            raise ImproperlyConfigured('AI_TIMEOUT_SECONDS must be between 1 and 10.')
        super().__init__(
            api_url=api_url or self.API_URL,
            api_key=key,
            model=model or os.getenv('AI_MODEL', self.DEFAULT_MODEL),
            timeout=timeout_seconds,
            allow_mock_fallback=allow_mock_fallback,
        )

    def _build_request_body(self, task_name, instructions, payload, schema):
        return {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': instructions},
                {'role': 'user', 'content': json.dumps(
                    {'task': task_name, 'data': payload},
                    ensure_ascii=False, separators=(',', ':'),
                )},
            ],
            'response_format': {
                'type': 'json_schema',
                'json_schema': {
                    'name': task_name,
                    'strict': True,
                    'schema': schema,
                },
            },
            'max_completion_tokens': self.max_completion_tokens,
            'stream': False,
        }

    def _call_or_fallback(self, name, instructions, payload, schema, fallback):
        result = super()._call_or_fallback(name, instructions, payload, schema, fallback)
        if not isinstance(result, dict):
            raise AIProviderError('AI provider returned an invalid result object.')
        if result.get('provider') == 'mock-fallback':
            result.pop('model', None)
            return result
        # Provenance always comes from this adapter, never from model content.
        result.pop('provider', None)
        result.pop('model', None)
        result['provider'] = 'groq'
        result['model'] = self.model
        return result
