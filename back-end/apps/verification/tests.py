import uuid
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.careers.models import CareerTrack
from apps.competencies.models import Competency
from apps.credentials.models import Credential, Evidence
from apps.credentials.services import CredentialService

User = get_user_model()


class PublicVerificationAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='johndoe', email='john@example.com', first_name='John', last_name='Doe', password='Password123!'
        )
        self.track = CareerTrack.objects.create(title='Backend Engineering', slug='backend-engineering')
        self.comp = Competency.objects.create(
            career_track=self.track, title='Authentication & Security', slug='auth-security', order=1
        )
        self.credential = Credential.objects.create(
            user=self.user,
            competency=self.comp,
            status=Credential.Status.ISSUED,
            score=95.0,
            metadata={
                'student_name': 'John Doe',
                'competency_title': 'Authentication & Security',
                'career_track_title': 'Backend Engineering',
                'score': 95.0
            }
        )
        self.evidence = Evidence.objects.create(
            credential=self.credential,
            github_url='https://github.com/johndoe/auth-security-demo',
            demo_url='https://auth.johndoe.dev',
            notes='Full OAuth2 & JWT Implementation.'
        )

    def test_verify_credential_publicly_no_auth(self):
        """Recruiters should be able to verify valid credentials with 0 authentication."""
        url = reverse('verify-credential', args=[self.credential.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['credential_id']), str(self.credential.id))
        self.assertTrue(response.data['is_valid'])
        self.assertEqual(response.data['status'], 'issued')
        self.assertEqual(response.data['student_name'], 'John Doe')
        self.assertEqual(response.data['competency_title'], 'Authentication & Security')
        self.assertEqual(response.data['career_track_title'], 'Backend Engineering')
        self.assertEqual(response.data['score'], 95.0)
        self.assertEqual(len(response.data['evidences']), 1)
        self.assertEqual(
            response.data['evidences'][0]['github_url'],
            'https://github.com/johndoe/auth-security-demo'
        )

    def test_verify_revoked_credential(self):
        """Revoked credentials should return is_valid=False and status=revoked."""
        CredentialService.revoke_credential(self.credential.id, reason="Plagiarism detected")

        url = reverse('verify-credential', args=[self.credential.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_valid'])
        self.assertEqual(response.data['status'], 'revoked')

    def test_verify_nonexistent_credential(self):
        """Random nonexistent UUID should return 404."""
        random_id = uuid.uuid4()
        url = reverse('verify-credential', args=[random_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
