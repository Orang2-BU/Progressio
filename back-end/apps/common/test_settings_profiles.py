import os
import subprocess
import sys
from pathlib import Path
from unittest import TestCase


BACKEND_DIR = Path(__file__).resolve().parents[2]
SETTING_ENV = (
    'APP_ENV', 'SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS', 'CORS_ALLOWED_ORIGINS',
    'CSRF_TRUSTED_ORIGINS', 'EMAIL_BACKEND', 'ENABLE_EMAIL', 'EMAIL_HOST',
    'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD', 'EMAIL_PORT', 'EMAIL_USE_TLS',
    'DB_ENGINE',
    'DEFAULT_FROM_EMAIL', 'TRUST_X_FORWARDED_PROTO',
    'SECURE_HSTS_SECONDS', 'SECURE_HSTS_INCLUDE_SUBDOMAINS', 'SECURE_HSTS_PRELOAD',
    'AI_PROVIDER', 'BLOCKCHAIN_PROVIDER', 'OPENAI_API_KEY', 'AI_ALLOW_MOCK_FALLBACK',
    'BLOCKCHAIN_SERVICE_URL',
)


class SettingsProfileTests(TestCase):
    def run_manage(self, *args, **updates):
        env = os.environ.copy()
        env['PYTHON_DOTENV_DISABLED'] = 'true'
        for name in SETTING_ENV:
            env.pop(name, None)
        env.update({name: str(value) for name, value in updates.items()})
        return subprocess.run(
            [sys.executable, 'manage.py', *args], cwd=BACKEND_DIR,
            env=env, capture_output=True, text=True,
        )

    def test_local_profile_starts_with_development_defaults(self):
        result = self.run_manage('check', APP_ENV='local')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_profile_must_be_selected_explicitly(self):
        result = self.run_manage('check')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Set APP_ENV explicitly', result.stderr)

    def test_production_rejects_missing_settings_and_development_key(self):
        missing = self.run_manage('check', APP_ENV='production')
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn('requires: SECRET_KEY', missing.stderr)

        fallback = self.run_manage(
            'check', APP_ENV='production',
            SECRET_KEY='django-insecure-local-only-development-key',
            ALLOWED_HOSTS='api.example.com', CORS_ALLOWED_ORIGINS='https://app.example.com',
            CSRF_TRUSTED_ORIGINS='https://app.example.com',
            DB_NAME='progressio_test', DB_USER='progressio_test',
            DB_PASSWORD='synthetic-test-only-password', DB_HOST='db.example.com',
        )
        self.assertNotEqual(fallback.returncode, 0)
        self.assertIn('Production SECRET_KEY', fallback.stderr)

        missing_providers = self.run_manage(
            'check', APP_ENV='production',
            SECRET_KEY='Synthetic-test-only-secret-0123456789-ABCDEFGHIJKLMNOP',
            ALLOWED_HOSTS='api.example.com', CORS_ALLOWED_ORIGINS='https://app.example.com',
            CSRF_TRUSTED_ORIGINS='https://app.example.com',
            DB_NAME='progressio_test', DB_USER='progressio_test',
            DB_PASSWORD='synthetic-test-only-password', DB_HOST='db.example.com',
        )
        self.assertNotEqual(missing_providers.returncode, 0)
        self.assertIn('AI_PROVIDER', missing_providers.stderr)

    def test_production_rejects_debug_and_wildcard(self):
        base = {
            'APP_ENV': 'production',
            'SECRET_KEY': 'Synthetic-test-only-secret-0123456789-ABCDEFGHIJKLMNOP',
            'CORS_ALLOWED_ORIGINS': 'https://app.example.com',
            'CSRF_TRUSTED_ORIGINS': 'https://app.example.com',
            'DB_NAME': 'progressio_test',
            'DB_USER': 'progressio_test',
            'DB_PASSWORD': 'synthetic-test-only-password',
            'DB_HOST': 'db.example.com',
            'AI_PROVIDER': 'mock',
            'BLOCKCHAIN_PROVIDER': 'mock',
        }
        debug = self.run_manage('check', **base, DEBUG='True', ALLOWED_HOSTS='api.example.com')
        self.assertNotEqual(debug.returncode, 0)
        self.assertIn('DEBUG must be False', debug.stderr)
        wildcard = self.run_manage('check', **base, DEBUG='False', ALLOWED_HOSTS='*')
        self.assertNotEqual(wildcard.returncode, 0)
        self.assertIn('ALLOWED_HOSTS', wildcard.stderr)
        subdomain_wildcard = self.run_manage(
            'check', **base, DEBUG='False', ALLOWED_HOSTS='.example.com',
        )
        self.assertNotEqual(subdomain_wildcard.returncode, 0)
        self.assertIn('ALLOWED_HOSTS', subdomain_wildcard.stderr)
        bad_origin_settings = {
            **base,
            'DEBUG': 'False',
            'ALLOWED_HOSTS': 'api.example.com',
            'CORS_ALLOWED_ORIGINS': 'https://*.example.com',
        }
        bad_origin = self.run_manage('check', **bad_origin_settings)
        self.assertNotEqual(bad_origin.returncode, 0)
        self.assertIn('CORS_ALLOWED_ORIGINS', bad_origin.stderr)
        malformed_port = self.run_manage(
            'check', **{**base, 'DEBUG': 'False', 'ALLOWED_HOSTS': 'api.example.com',
                       'CORS_ALLOWED_ORIGINS': 'https://app.example.com:bad'},
        )
        self.assertNotEqual(malformed_port.returncode, 0)
        self.assertIn('CORS_ALLOWED_ORIGINS', malformed_port.stderr)
        malformed_host = self.run_manage(
            'check', **{**base, 'DEBUG': 'False', 'ALLOWED_HOSTS': 'https://api.example.com'},
        )
        self.assertNotEqual(malformed_host.returncode, 0)
        self.assertIn('ALLOWED_HOSTS', malformed_host.stderr)

    def test_deploy_check_passes_with_synthetic_production_settings(self):
        result = self.run_manage(
            'check', '--deploy', APP_ENV='production',
            SECRET_KEY='Synthetic-test-only-secret-0123456789-ABCDEFGHIJKLMNOP',
            DEBUG='False', ALLOWED_HOSTS='api.example.com',
            CORS_ALLOWED_ORIGINS='https://app.example.com',
            CSRF_TRUSTED_ORIGINS='https://app.example.com',
            DB_NAME='progressio_test', DB_USER='progressio_test',
            DB_PASSWORD='synthetic-test-only-password', DB_HOST='db.example.com',
            SECURE_HSTS_INCLUDE_SUBDOMAINS='True', SECURE_HSTS_PRELOAD='True',
            AI_PROVIDER='openai', OPENAI_API_KEY='synthetic-test-only-openai-key',
            BLOCKCHAIN_PROVIDER='http', BLOCKCHAIN_SERVICE_URL='https://signer.example.com',
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('WARNINGS', result.stdout + result.stderr)

    def test_production_email_requires_smtp_when_enabled(self):
        required = {
            'APP_ENV': 'production',
            'SECRET_KEY': 'Synthetic-test-only-secret-0123456789-ABCDEFGHIJKLMNOP',
            'DEBUG': 'False',
            'ALLOWED_HOSTS': 'api.example.com',
            'CORS_ALLOWED_ORIGINS': 'https://app.example.com',
            'CSRF_TRUSTED_ORIGINS': 'https://app.example.com',
            'DB_NAME': 'progressio_test',
            'DB_USER': 'progressio_test',
            'DB_PASSWORD': 'synthetic-test-only-password',
            'DB_HOST': 'db.example.com',
            'AI_PROVIDER': 'mock',
            'BLOCKCHAIN_PROVIDER': 'mock',
            'ENABLE_EMAIL': 'True',
        }
        missing = self.run_manage('check', **required)
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn('ENABLE_EMAIL=True with SMTP requires', missing.stderr)

        console = self.run_manage(
            'check', **required,
            EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend',
        )
        self.assertNotEqual(console.returncode, 0)
        self.assertIn('requires the SMTP email backend', console.stderr)

        configured = self.run_manage(
            'check', **required, EMAIL_HOST='smtp.example.com',
            EMAIL_HOST_USER='synthetic-user', EMAIL_HOST_PASSWORD='synthetic-password',
            DEFAULT_FROM_EMAIL='Progressio <noreply@example.com>',
        )
        self.assertEqual(configured.returncode, 0, configured.stderr)

        missing_sender = self.run_manage(
            'check', **required, EMAIL_HOST='smtp.example.com',
            EMAIL_HOST_USER='synthetic-user', EMAIL_HOST_PASSWORD='synthetic-password',
        )
        self.assertNotEqual(missing_sender.returncode, 0)
        self.assertIn('DEFAULT_FROM_EMAIL', missing_sender.stderr)

    def test_production_rejects_sqlite(self):
        result = self.run_manage(
            'check', APP_ENV='production',
            SECRET_KEY='Synthetic-test-only-secret-0123456789-ABCDEFGHIJKLMNOP',
            ALLOWED_HOSTS='api.example.com', CORS_ALLOWED_ORIGINS='https://app.example.com',
            CSRF_TRUSTED_ORIGINS='https://app.example.com',
            DB_NAME='progressio_test', DB_USER='progressio_test',
            DB_PASSWORD='synthetic-test-only-password', DB_HOST='db.example.com',
            DB_ENGINE='sqlite', AI_PROVIDER='mock', BLOCKCHAIN_PROVIDER='mock',
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('DB_ENGINE must be', result.stderr)
