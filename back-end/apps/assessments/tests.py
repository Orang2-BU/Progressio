from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.careers.models import CareerTrack
from apps.competencies.models import Competency
from apps.skills.models import Skill
from apps.learning.models import SkillProgress, CompetencyProgress
from .models import Assessment, Submission, DiagnosticAttempt, DiagnosticQuestion

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
            max_score=100,
            grading_config={'answer_key': {'q1': 'A', 'q2': 'B', 'q3': 'C', 'q4': 'D'}},
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
        self.assertNotIn('grading_config', response.data)

    def test_submit_assessment_authenticated_passed(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('assessment-submit', args=[self.assessment.id])
        payload = {
            'content': {'answers': {'q1': 'A', 'q2': 'B', 'q3': 'C', 'q4': 'wrong'}},
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'completed')
        self.assertEqual(response.data['score'], 75.0)
        self.assertTrue(response.data['is_passed'])
        self.assertIn('3 of 4 answers correct', response.data['feedback'])

        # Verify SkillProgress updated
        progress = SkillProgress.objects.get(user=self.user, skill=self.skill)
        self.assertEqual(progress.mastery, 75.0)
        self.assertEqual(progress.xp, 100)
        self.assertEqual(progress.confidence, 0.75)

        # Verify CompetencyProgress updated
        comp_prog = CompetencyProgress.objects.get(user=self.user, competency=self.comp)
        self.assertEqual(comp_prog.score, 75.0)

    def test_submit_assessment_failed(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('assessment-submit', args=[self.assessment.id])
        payload = {
            'content': {'answers': {'q1': 'A'}},
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['score'], 25.0)
        self.assertFalse(response.data['is_passed'])

    def test_client_cannot_override_score(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('assessment-submit', args=[self.assessment.id]),
            {'content': {'answers': {}}, 'score': 100},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Submission.objects.count(), 0)

    def test_submission_payload_size_is_limited(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('assessment-submit', args=[self.assessment.id]),
            {'content': {'code': 'x' * 200_001}},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Submission.objects.count(), 0)

    def test_submit_assessment_unauthenticated(self):
        url = reverse('assessment-submit', args=[self.assessment.id])
        response = self.client.post(url, {'content': {}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DiagnosticAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='diagnostic_student',
            email='diagnostic@example.com',
            password='Password123!',
            role='student',
        )
        self.track = CareerTrack.objects.create(title='Backend Engineering', slug='backend-engineering')
        self.comp = Competency.objects.create(
            career_track=self.track,
            title='Backend Foundations',
            slug='backend-foundations',
            order=1,
        )
        self.rest_skill = Skill.objects.create(
            competency=self.comp, title='REST API', slug='diagnostic-rest-api'
        )
        self.auth_skill = Skill.objects.create(
            competency=self.comp, title='Authentication', slug='diagnostic-authentication'
        )
        self.questions = [
            DiagnosticQuestion.objects.create(
                career_track=self.track,
                skill=self.rest_skill,
                prompt='Which HTTP method creates a resource?',
                options=[{'value': 'POST', 'label': 'POST'}, {'value': 'GET', 'label': 'GET'}],
                correct_answer='POST',
                order=1,
            ),
            DiagnosticQuestion.objects.create(
                career_track=self.track,
                skill=self.rest_skill,
                prompt='Which status code commonly means created?',
                options=[{'value': '201', 'label': '201'}, {'value': '404', 'label': '404'}],
                correct_answer='201',
                order=2,
            ),
            DiagnosticQuestion.objects.create(
                career_track=self.track,
                skill=self.auth_skill,
                prompt='What is commonly used for bearer authentication?',
                options=[{'value': 'JWT', 'label': 'JWT'}, {'value': 'CSS', 'label': 'CSS'}],
                correct_answer='JWT',
                order=3,
            ),
        ]
        self.client.force_authenticate(user=self.user)

    def test_question_list_never_exposes_answer_key(self):
        response = self.client.get(reverse('diagnostic-question-list', args=[self.track.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertNotIn('correct_answer', response.data[0])
        self.assertNotIn('explanation', response.data[0])

    def test_submit_diagnostic_grades_and_updates_skill_progress(self):
        answers = {
            str(self.questions[0].id): 'POST',
            str(self.questions[1].id): 'wrong',
            str(self.questions[2].id): 'JWT',
        }
        response = self.client.post(
            reverse('diagnostic-submit', args=[self.track.id]),
            {'answers': answers},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertAlmostEqual(response.data['overall_score'], 66.7)
        self.assertEqual(response.data['recommended_skill_ids'], [self.rest_skill.id])
        self.assertTrue(DiagnosticAttempt.objects.filter(user=self.user).exists())

        rest_progress = SkillProgress.objects.get(user=self.user, skill=self.rest_skill)
        auth_progress = SkillProgress.objects.get(user=self.user, skill=self.auth_skill)
        self.assertEqual(rest_progress.mastery, 50.0)
        self.assertEqual(auth_progress.mastery, 100.0)
        self.assertEqual(rest_progress.xp, 0)

        latest = self.client.get(
            reverse('diagnostic-latest'),
            {'career_track': self.track.id},
        )
        self.assertEqual(latest.status_code, status.HTTP_200_OK)
        self.assertEqual(latest.data['id'], response.data['id'])

    def test_submit_requires_all_questions(self):
        response = self.client.post(
            reverse('diagnostic-submit', args=[self.track.id]),
            {'answers': {str(self.questions[0].id): 'POST'}},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DiagnosticAttempt.objects.count(), 0)
