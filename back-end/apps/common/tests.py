from django.test import TestCase
from django.urls import reverse
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework import status
from apps.assessments.models import Assessment, DiagnosticQuestion
from apps.careers.models import CareerTrack


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
        call_command('seed_demo', verbosity=0)
        call_command('seed_demo', verbosity=0)
        self.assertEqual(CareerTrack.objects.filter(slug='backend-engineering').count(), 1)
        self.assertEqual(DiagnosticQuestion.objects.count(), 8)
        self.assertEqual(
            Assessment.objects.filter(title='Build a Secure JWT + RBAC API').count(),
            1,
        )
