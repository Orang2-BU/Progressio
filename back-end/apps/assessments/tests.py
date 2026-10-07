from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from typing import Any, cast
from rest_framework.test import APIClient
from rest_framework.response import Response as APIResponse
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

    def post_api(self, url, data):
        """Keep the DRF response type explicit for Django's broad test-client stubs."""
        return cast(APIResponse, self.client.post(url, data, format='json'))

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

    def test_request_replay_conflict_recovery_and_user_isolation(self):
        import uuid
        self.client.force_authenticate(user=self.user)
        body = {'request_id': str(uuid.uuid4()), 'content': {'answers': {'q1': 'A', 'q2': 'B', 'q3': 'C', 'q4': 'D'}}}
        url = reverse('assessment-submit', args=[self.assessment.pk])
        first = self.client.post(url, body, format='json')
        second = self.client.post(url, body, format='json')
        self.assertEqual(first.status_code, 201)
        self.assertEqual(first.data['id'], second.data['id'])
        self.assertEqual(Submission.objects.count(), 1)
        self.assertEqual(SkillProgress.objects.get(user=self.user, skill=self.skill).xp, 100)
        self.assertEqual(first.data['evaluation']['provider'], 'rules')
        self.assessment.passing_score = 101; self.assessment.save()
        self.assertTrue(self.client.get(reverse('submission-detail', args=[first.data['id']])).data['is_passed'])
        latest = self.client.get(reverse('submission-list'), {'request_id': body['request_id']})
        self.assertEqual(latest.data['results'][0]['id'], first.data['id'])
        body['content']['answers']['q1'] = 'wrong'
        self.assertEqual(self.client.post(url, body, format='json').status_code, 400)
        self.client.force_authenticate(user=User.objects.create_user(username='other-results'))
        self.assertEqual(self.client.get(reverse('submission-detail', args=[first.data['id']])).status_code, 404)
        self.assertEqual(self.client.get(reverse('submission-list')).data['count'], 0)
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get(reverse('submission-list')).status_code, 401)

    @override_settings(THROTTLE_RATES={**settings.THROTTLE_RATES, 'expensive_assessment': '1/hour'})
    def test_assessment_budget_is_per_user_and_allows_idempotent_retries(self):
        import uuid

        url = reverse('assessment-submit', args=[self.assessment.pk])
        request_id = str(uuid.uuid4())
        body = {
            'request_id': request_id,
            'content': {'answers': {'q1': 'A', 'q2': 'B', 'q3': 'C', 'q4': 'D'}},
        }

        self.client.force_authenticate(user=self.user)
        first = self.post_api(url, body)
        replay = self.post_api(url, body)
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(replay.status_code, status.HTTP_201_CREATED)
        self.assertEqual(first.data['id'], replay.data['id'])
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(replay.status_code, status.HTTP_201_CREATED)
        self.assertEqual(cast(Any, Submission).objects.filter(user=self.user).count(), 1)
        self.assertEqual(
            cast(Any, SkillProgress).objects.get(user=self.user, skill=self.skill).xp,
            100,
        )

        new_work = self.post_api(
            url, {'request_id': str(uuid.uuid4()), 'content': body['content']}
        )
        self.assertEqual(new_work.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        retry_seconds = new_work.data['retry_after_seconds']
        self.assertEqual(new_work['Retry-After'], str(retry_seconds))

        other_user = User.objects.create_user(username='other-budget-user')
        self.client.force_authenticate(user=other_user)
        isolated = self.post_api(
            url, {'request_id': str(uuid.uuid4()), 'content': body['content']}
        )
        self.assertEqual(isolated.status_code, status.HTTP_201_CREATED)

    def test_provider_failure_rolls_back_and_retry_uses_same_id(self):
        import uuid
        from unittest.mock import patch
        self.client.force_authenticate(user=self.user)
        self.assessment.evaluation_mode = 'ai'; self.assessment.save()
        url = reverse('assessment-submit', args=[self.assessment.pk])
        body = {'request_id': str(uuid.uuid4()), 'content': {'text': 'Example evidence'}}
        with patch('apps.ai.services.AIService.get_adapter', side_effect=RuntimeError('secret provider detail')):
            response = self.client.post(url, body, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertNotIn('secret', str(response.data))
        self.assertEqual(Submission.objects.count(), 0)
        with patch('apps.assessments.services.AssessmentEvaluationService._evaluate_with_ai', return_value={'score': 90, 'provider': 'mock-fallback'}):
            result = self.client.post(url, body, format='json')
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.data['evaluation']['provider'], 'mock-fallback')
        self.assertEqual(self.client.post(url, {'content': {'github_url': 'https://example.org'}}, format='json').status_code, 400)
        self.assertEqual(self.client.post(url, {'content': {'text': 'evidence', 'github_url': 'javascript:alert(1)'}}, format='json').status_code, 400)
        with patch('apps.assessments.services.AssessmentEvaluationService._evaluate_with_ai', return_value={'score': float('nan')}):
            invalid = self.client.post(url, {'request_id': str(uuid.uuid4()), 'content': {'text': 'evidence'}}, format='json')
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(Submission.objects.count(), 1)

    def test_public_quiz_requires_complete_valid_answers(self):
        self.client.force_authenticate(user=self.user)
        self.assessment.questions = [{'id': 'q1', 'prompt': 'Question', 'options': [{'value': 'A', 'label': 'First'}, {'value': 'B', 'label': 'Second'}]}]
        self.assessment.grading_config = {'answer_key': {'q1': 'A'}}
        self.assessment.save()
        url = reverse('assessment-submit', args=[self.assessment.pk])
        for answers in ({}, {'q1': 'unsafe'}, {'q1': 'A', 'unknown': 'A'}):
            self.assertEqual(self.client.post(url, {'content': {'answers': answers}}, format='json').status_code, 400)
        result = self.client.post(url, {'content': {'answers': {'q1': 'B'}}}, format='json')
        self.assertEqual(result.status_code, 201)
        self.assertFalse(result.data['is_passed'])
        self.assertEqual(result.data['score'], 0)


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

    def test_latest_repeated_attempts_and_isolation(self):
        from django.utils import timezone
        latest_url = reverse('diagnostic-latest')
        self.assertEqual(self.client.get(latest_url).status_code, 404)
        url = reverse('diagnostic-submit', args=[self.track.id])
        correct = {str(q.id): q.correct_answer for q in self.questions}
        first = self.client.post(url, {'answers': correct}, format='json')
        second = self.client.post(url, {'answers': {str(q.id): '' for q in self.questions}}, format='json')
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        self.assertEqual(second.data['overall_score'], 0)
        self.assertEqual(SkillProgress.objects.get(user=self.user, skill=self.rest_skill).mastery, 100)
        self.assertEqual(SkillProgress.objects.get(user=self.user, skill=self.rest_skill).xp, 0)
        now = timezone.now()
        DiagnosticAttempt.objects.filter(user=self.user).update(completed_at=now, created_at=now)
        other = User.objects.create_user(username='other_diagnostic')
        other_track = CareerTrack.objects.create(title='Other', slug='other-diagnostic')
        DiagnosticAttempt.objects.create(user=other, career_track=self.track, completed_at=now)
        unrelated = DiagnosticAttempt.objects.create(user=self.user, career_track=other_track, completed_at=now)
        self.assertEqual(self.client.get(latest_url, {'career_track': self.track.id}).data['id'], second.data['id'])
        self.assertEqual(self.client.get(latest_url).data['id'], unrelated.id)
        self.assertEqual(self.client.get(latest_url, {'career_track': 99999}).status_code, 404)
        for invalid in ('', 'oops', '-1', '0', '9' * 40):
            self.assertEqual(self.client.get(latest_url, {'career_track': invalid}).status_code, 400)
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get(latest_url).status_code, 401)

    def test_question_list_matches_grading_track(self):
        other_track = CareerTrack.objects.create(title='Other', slug='other-question')
        self.questions[0].career_track = other_track
        self.questions[0].save()
        response = self.client.get(reverse('diagnostic-question-list', args=[other_track.id]))
        self.assertEqual(response.data, [])
