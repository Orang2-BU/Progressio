from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class APIDocumentationAndHealthTests(TestCase):
    """
    Unit tests to verify API endpoints, health check, OpenAPI 3.0 schema, and docs.
    """

    def setUp(self):
        self.client = APIClient()

    def test_health_check_endpoint(self):
        """Test health check endpoint returns 200 OK and valid JSON data."""
        url = reverse('core:health-check')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 'ok')
        self.assertEqual(response.data.get('service'), 'Progressio API')
        self.assertEqual(response.data.get('version'), '1.0.0')
        self.assertIn('message', response.data)

    def test_openapi_schema_endpoint(self):
        """Test OpenAPI 3.0 schema generation endpoint."""
        url = reverse('schema')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify OpenAPI 3.0 schema contents
        self.assertIn('openapi', response.content.decode('utf-8'))
        self.assertIn('Progressio API', response.content.decode('utf-8'))

    def test_swagger_ui_endpoint(self):
        """Test Swagger UI endpoint returns 200 OK."""
        url = reverse('swagger-ui')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('text/html', response['content-type'])

    def test_redoc_ui_endpoint(self):
        """Test Redoc UI endpoint returns 200 OK."""
        url = reverse('redoc')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('text/html', response['content-type'])

    def test_root_redirects_to_docs(self):
        """Test root URL redirects to Swagger docs."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, '/api/docs/')
