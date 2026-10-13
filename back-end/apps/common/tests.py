import os
from io import StringIO
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.core.management import call_command
from django.core.management.base import CommandError
from rest_framework.test import APIClient
from rest_framework import status
from apps.assessments.models import Assessment, DiagnosticQuestion
from apps.careers.models import CareerTrack
from apps.skills.models import Skill
from django.contrib.auth import get_user_model

User = get_user_model()


class ThrottleRateConfigurationTests(SimpleTestCase):
    def test_valid_aliases_are_accepted(self):
        from config.settings import throttle_rate

        with patch.dict(os.environ, {'THROTTLE_RATE_TEST': '10/min'}):
            self.assertEqual(throttle_rate('THROTTLE_RATE_TEST', '1/hour'), '10/min')

    def test_unknown_period_suffix_is_rejected(self):
        from config.settings import throttle_rate

        with patch.dict(os.environ, {'THROTTLE_RATE_TEST': '10/month'}):
            with self.assertRaises(ImproperlyConfigured):
                throttle_rate('THROTTLE_RATE_TEST', '1/hour')


class HealthCheckTests(TestCase):
    """Tests for health check and documentation endpoints."""

    def setUp(self):
        self.client = APIClient()

    def test_health_check_returns_200(self):
        """Health check should return 200 OK with correct payload."""
        response = self.client.get(reverse('health-check'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['service'], 'Progressio API')
        self.assertEqual(response.data['version'], '1.0.0')
        self.assertIn('message', response.data)

    def test_readiness_separates_liveness_from_unseeded_demo_catalog(self):
        self.assertEqual(self.client.get(reverse('health-check')).status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('readiness-check'))
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data['status'], 'not_ready')
        self.assertEqual(response.data['components']['database'], 'ok')
        self.assertEqual(response.data['components']['cache'], 'ok')
        self.assertEqual(response.data['components']['catalog'], 'unavailable')
        self.assertEqual(set(response.data), {'status', 'components'})

    def test_readiness_sanitizes_cache_and_database_failures(self):
        with patch('apps.common.views.caches') as mocked_caches:
            mocked_caches.__getitem__.side_effect = RuntimeError('synthetic redis credential')
            response = self.client.get(reverse('readiness-check'))
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data['components']['cache'], 'unavailable')
        self.assertNotIn('synthetic redis credential', str(response.data))

        with patch('apps.common.views.connection.cursor', side_effect=RuntimeError('synthetic database password')):
            response = self.client.get(reverse('readiness-check'))
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data['components']['database'], 'unavailable')
        self.assertNotIn('synthetic database password', str(response.data))

    def test_openapi_schema_endpoint(self):
        """OpenAPI schema should be generated successfully."""
        response = self.client.get(reverse('schema'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = response.content.decode('utf-8')
        self.assertIn('openapi', content)
        self.assertIn('Progressio API', content)

    def test_swagger_ui_endpoint(self):
        """Swagger UI should return 200 with HTML."""
        response = self.client.get(reverse('swagger-ui'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('text/html', response['content-type'])

    def test_redoc_ui_endpoint(self):
        """Redoc UI should return 200 with HTML."""
        response = self.client.get(reverse('redoc'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('text/html', response['content-type'])

    def test_root_redirects_to_docs(self):
        """Root URL should redirect to Swagger docs."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, '/api/docs/')

    def test_seed_demo_command_is_idempotent(self):
        """seed_demo now projects the curriculum package; running it twice is a no-op."""
        call_command('seed_demo', verbosity=0)
        counts = (
            CareerTrack.objects.count(),
            Skill.objects.count(),
            Assessment.objects.count(),
            DiagnosticQuestion.objects.count(),
        )

        call_command('seed_demo', verbosity=0)

        self.assertEqual(
            (
                CareerTrack.objects.count(),
                Skill.objects.count(),
                Assessment.objects.count(),
                DiagnosticQuestion.objects.count(),
            ),
            counts,
        )
        self.assertEqual(CareerTrack.objects.filter(slug='backend-engineering').count(), 1)

    def test_seed_demo_sources_the_curriculum_rather_than_defining_one(self):
        call_command('seed_demo', verbosity=0)

        track = CareerTrack.objects.get(slug='backend-engineering')
        self.assertEqual(track.curriculum_version, '0.1.0')
        self.assertTrue(track.is_managed)
        # Every skill came from the package, none hand-written by the command.
        self.assertTrue(Skill.objects.exists())
        self.assertFalse(Skill.objects.filter(is_managed=False).exists())
        self.assertTrue(User.objects.filter(username='student').exists())


class SeedDemoCommandTests(TestCase):
    def test_missing_or_invalid_curriculum_fails_without_creating_demo_accounts(self):
        with patch('apps.common.management.commands.seed_demo.available_tracks', return_value=[]):
            with self.assertRaises(CommandError):
                call_command('seed_demo', verbosity=0)
        self.assertFalse(User.objects.filter(username='student').exists())

        def import_track(track_id):
            if track_id == 'first':
                User.objects.create_user(username='partial-import')
                return type('ImportReport', (), {
                    'created': {}, 'updated': {}, 'warnings': [],
                })()
            from apps.curriculum.loader import CurriculumError
            raise CurriculumError('synthetic invalid package')

        with patch('apps.common.management.commands.seed_demo.available_tracks',
                   return_value=['first', 'broken']), \
                patch('apps.common.management.commands.seed_demo.import_track', side_effect=import_track):
            with self.assertRaises(CommandError):
                call_command('seed_demo', verbosity=0)
        self.assertFalse(User.objects.filter(username__in=['student', 'partial-import']).exists())

    def test_demo_preflight_checks_a_two_skill_demo_and_omits_provider_secrets(self):
        with self.assertRaises(CommandError):
            call_command('demo_preflight', stdout=StringIO(), stderr=StringIO())
        call_command('seed_demo', verbosity=0, stdout=StringIO())
        output = StringIO()
        call_command('demo_preflight', stdout=output)
        self.assertIn('two-skill competencies', output.getvalue())
        self.assertIn('Demo preflight passed.', output.getvalue())
        self.assertNotIn('GROQ_API_KEY', output.getvalue())
