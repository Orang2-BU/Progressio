from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.careers.models import CareerTrack
from apps.competencies.models import Competency
from apps.skills.models import Skill
from apps.learning.models import SkillProgress, CompetencyProgress
from .models import Assessment, Submission

User = get_user_model()


class AssessmentModelAndAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='student1', email='s1@example.com', password='Password123!', role='student'
        )
        self.track = CareerTrack.objects.create(title='Backend', slug='backend')
        self.comp = Competency.objects.create(
            career_track=self.track, title='API Dev', slug='api-dev', order=1
        )
        self.skill = Skill.objects.create(
            competency=self.comp, title='REST API', slug='rest-api',
            difficulty=Skill.Difficulty.BEGINNER, estimated_learning_minutes=60
        )
        self.assessment = Assessment.objects.create(
            skill=self.skill,
            title='REST API Quiz',
            assessment_type=Assessment.AssessmentType.QUIZ,
            instructions='Answer the questions carefully.',
            passing_score=70,
            max_score=100
        )

    def test_assessment_list(self):
        url = reverse('assessment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'REST API Quiz')

    def test_assessment_detail(self):
        url = reverse('assessment-detail', args=[self.assessment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'REST API Quiz')
        self.assertEqual(response.data['instructions'], 'Answer the questions carefully.')

    def test_submit_assessment_authenticated_passed(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('assessment-submit', args=[self.assessment.id])
        payload = {
            'content': {'answers': {'q1': 'A', 'q2': 'B', 'q3': 'C', 'q4': 'D'}},
            'score': 85.0
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'completed')
        self.assertEqual(response.data['score'], 85.0)
        self.assertTrue(response.data['is_passed'])
        self.assertIn('Great work', response.data['feedback'])

        # Verify SkillProgress updated
        progress = SkillProgress.objects.get(user=self.user, skill=self.skill)
        self.assertEqual(progress.mastery, 85.0)
        self.assertEqual(progress.xp, 100)
        self.assertEqual(progress.confidence, 0.85)

        # Verify CompetencyProgress updated
        comp_prog = CompetencyProgress.objects.get(user=self.user, competency=self.comp)
        self.assertEqual(comp_prog.score, 85.0)

    def test_submit_assessment_failed(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('assessment-submit', args=[self.assessment.id])
        payload = {
            'content': {'answers': {'q1': 'A'}},
            'score': 50.0
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['score'], 50.0)
        self.assertFalse(response.data['is_passed'])

    def test_submit_assessment_unauthenticated(self):
        url = reverse('assessment-submit', args=[self.assessment.id])
        response = self.client.post(url, {'content': {}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
