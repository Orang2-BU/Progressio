from django.test import TestCase
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
            assessment_type=Assessment.AssessmentType.QUIZ,
            passing_score=70, max_score=100
        )
        submission = Submission.objects.create(
            user=self.user, assessment=assessment,
            content={'answers': {'q1': 'Docker image build', 'q2': 'Docker compose up'}},
            status=Submission.Status.SUBMITTED
        )

        result = evaluate_submission_ai_task(submission.id)
        self.assertIn(f"Submission {submission.id} evaluated", result)

        submission.refresh_from_db()
        self.assertEqual(submission.status, Submission.Status.COMPLETED)
        self.assertIsNotNone(submission.score)
        self.assertIn('AI Evaluation', submission.feedback)
