from django.test import TestCase
from django.urls import reverse
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework import status
from apps.assessments.models import Assessment, DiagnosticQuestion
from apps.careers.models import CareerTrack
from apps.skills.models import Skill
from django.contrib.auth import get_user_model

User = get_user_model()


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
