from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.careers.models import CareerTrack
from apps.competencies.models import Competency
from apps.skills.models import Skill
from apps.learning.models import SkillProgress
from apps.assessments.models import Assessment, Submission
from .tasks import evaluate_submission_ai_task
from .services import AIService
from .adapters.openai_adapter import OpenAIAdapter
from unittest.mock import MagicMock, patch
import json
import os

User = get_user_model()


class AIServicesTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='ai_student', email='ai@example.com', password='Password123!', role='student'
        )
        self.track = CareerTrack.objects.create(title='Cloud Engineering', slug='cloud-engineering')
        self.comp = Competency.objects.create(
            career_track=self.track, title='Containers', slug='containers', order=1
        )
        self.skill1 = Skill.objects.create(
            competency=self.comp, title='Docker Containers', slug='docker-containers',
            difficulty=Skill.Difficulty.BEGINNER, estimated_learning_minutes=60
        )
        self.skill2 = Skill.objects.create(
            competency=self.comp, title='Kubernetes Orchestration', slug='k8s-orchestration',
            difficulty=Skill.Difficulty.ADVANCED, estimated_learning_minutes=180
        )

    def test_skill_gap_analysis_endpoint(self):
        self.client.force_authenticate(user=self.user)
        # Give user mastery in skill 1 only
        SkillProgress.objects.create(user=self.user, skill=self.skill1, mastery=80.0, xp=150)

        url = reverse('ai-skill-gap-analysis')
        payload = {'career_track_id': self.track.id}
        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['target_career_track'], 'Cloud Engineering')
        self.assertEqual(response.data['match_percentage'], 50.0)  # 1/2 skills acquired
        self.assertEqual(len(response.data['acquired_skills']), 1)
        self.assertEqual(len(response.data['missing_skills']), 1)
        self.assertEqual(response.data['missing_skills'][0]['title'], 'Kubernetes Orchestration')
        self.assertIn('ai_insights', response.data)

    def test_learning_recommendations_endpoint(self):
        self.client.force_authenticate(user=self.user)
        # User has a skill in progress (mastery 40%)
        SkillProgress.objects.create(user=self.user, skill=self.skill1, mastery=40.0, xp=50)

        url = reverse('ai-recommendations')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['student_name'], 'ai_student')
        self.assertEqual(len(response.data['recommendations']), 1)
        self.assertIn('Docker Containers', response.data['recommendations'][0]['title'])

    def test_ai_evaluation_celery_task(self):
        assessment = Assessment.objects.create(
            skill=self.skill1, title='Docker Quiz',
            assessment_type=Assessment.AssessmentType.CHALLENGE,
            evaluation_mode=Assessment.EvaluationMode.AI,
            passing_score=70, max_score=100
        )
        submission = Submission.objects.create(
            user=self.user, assessment=assessment,
            content={
                'code': 'authentication jwt permission\n' + ('x = 1\n' * 60),
                'test_output': 'pytest test_authentication: passed',
                'readme': 'README usage documentation and error handling',
            },
            status=Submission.Status.SUBMITTED
        )

        result = evaluate_submission_ai_task(submission.id)
        self.assertIn(f"Submission {submission.id} evaluated", result)

        submission.refresh_from_db()
        self.assertEqual(submission.status, Submission.Status.COMPLETED)
        self.assertIsNotNone(submission.score)
        self.assertIn('Mock evaluation', submission.feedback)
        self.assertTrue(submission.is_passed)
        progress = SkillProgress.objects.get(user=self.user, skill=self.skill1)
        self.assertEqual(progress.xp, 100)

    def test_openai_provider_requires_api_key(self):
        with patch.dict(os.environ, {'AI_PROVIDER': 'openai'}, clear=False):
            os.environ.pop('OPENAI_API_KEY', None)
            with self.assertRaises(ImproperlyConfigured):
                AIService.get_adapter()

    def test_openai_adapter_parses_structured_response(self):
        expected = {'score': 82, 'feedback': 'Solid implementation'}
        fake_response = MagicMock()
        fake_response.__enter__.return_value.read.return_value = json.dumps({
            'output': [{
                'content': [{'type': 'output_text', 'text': json.dumps(expected)}]
            }]
        }).encode('utf-8')

        adapter = OpenAIAdapter(api_key='test-key', model='test-model')
        with patch('apps.ai.adapters.openai_adapter.urlopen', return_value=fake_response) as mocked:
            result = adapter._request_json(
                'test_result',
                'Return the result.',
                {'input': 'data'},
                {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'score': {'type': 'number'},
                        'feedback': {'type': 'string'},
                    },
                    'required': ['score', 'feedback'],
                },
            )

        self.assertEqual(result, expected)
        request = mocked.call_args.args[0]
        sent_body = json.loads(request.data.decode('utf-8'))
        self.assertEqual(sent_body['model'], 'test-model')
        self.assertEqual(sent_body['text']['format']['type'], 'json_schema')
