from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.careers.models import CareerTrack
from apps.competencies.models import Competency
from apps.learning.models import CompetencyProgress
from apps.skills.models import Skill
from apps.assessments.models import Assessment, Submission
from django.utils import timezone
from .models import Credential, Evidence

User = get_user_model()


class CredentialAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='student_cred', email='cred@example.com', password='Password123!', role='student'
        )
        self.track = CareerTrack.objects.create(title='Backend Track', slug='backend-track')
        self.comp = Competency.objects.create(
            career_track=self.track, title='Database Engineering', slug='database-engineering', order=1
        )
        self.skill = Skill.objects.create(
            competency=self.comp, title='SQL Fundamentals', slug='credential-sql-fundamentals'
        )
        self.assessment = Assessment.objects.create(
            skill=self.skill,
            title='SQL Project',
            assessment_type=Assessment.AssessmentType.PROJECT,
            passing_score=70,
            max_score=100,
        )

    def create_passed_submission(self, score=88.0):
        return Submission.objects.create(
            user=self.user,
            assessment=self.assessment,
            status=Submission.Status.COMPLETED,
            score=score,
            submitted_at=timezone.now(),
        )

    def test_issue_credential_ineligible_returns_400(self):
        """Should fail if student has not reached 70% score."""
        self.client.force_authenticate(user=self.user)
        # Record low progress (50%)
        CompetencyProgress.objects.create(
            user=self.user, competency=self.comp, score=50.0, confidence=0.5
        )

        url = reverse('credential-issue')
        response = self.client.post(url, {'competency_id': self.comp.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Minimum required score', str(response.data))

    def test_issue_credential_eligible_success(self):
        """Should issue credential and attach evidence when score >= 70%."""
        self.client.force_authenticate(user=self.user)
        # Record passing progress (88%)
        CompetencyProgress.objects.create(
            user=self.user, competency=self.comp, score=88.0, confidence=0.88
        )
        submission = self.create_passed_submission()

        url = reverse('credential-issue')
        payload = {
            'competency_id': self.comp.id,
            'github_url': 'https://github.com/student/progressio-db-project',
            'demo_url': 'https://progressio-db.demo.app',
            'notes': 'Implemented SQL optimization, indexing, and partitioning.',
            'submission_id': submission.id,
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'issued')
        self.assertEqual(response.data['score'], 88.0)
        self.assertTrue(response.data['is_valid'])
        self.assertEqual(len(response.data['evidences']), 1)
        self.assertEqual(
            response.data['evidences'][0]['github_url'],
            'https://github.com/student/progressio-db-project'
        )
        self.assertEqual(response.data['evidences'][0]['submission'], submission.id)

    def test_issue_requires_a_passed_assessment(self):
        self.client.force_authenticate(user=self.user)
        CompetencyProgress.objects.create(
            user=self.user, competency=self.comp, score=90.0, confidence=0.9
        )
        response = self.client.post(
            reverse('credential-issue'), {'competency_id': self.comp.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('passing assessment', str(response.data))

    def test_list_and_detail_credentials(self):
        self.client.force_authenticate(user=self.user)
        CompetencyProgress.objects.create(
            user=self.user, competency=self.comp, score=90.0, confidence=0.9
        )
        self.create_passed_submission(score=90.0)
        issue_res = self.client.post(reverse('credential-issue'), {'competency_id': self.comp.id}, format='json')
        cred_id = issue_res.data['id']

        # List
        list_res = self.client.get(reverse('credential-list'))
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        results = list_res.data.get('results', list_res.data)
        self.assertEqual(len(results), 1)

        # Detail
        detail_res = self.client.get(reverse('credential-detail', args=[cred_id]))
        self.assertEqual(detail_res.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_res.data['competency_title'], 'Database Engineering')
