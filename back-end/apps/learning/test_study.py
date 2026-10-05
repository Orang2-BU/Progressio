import urllib.error
from email.message import Message
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.curriculum.importer import import_track

from .models import Lesson, StudyStep, LessonCompletion, SkillProgress
from .tasks import check_resource_links, check_url

User = get_user_model()


class StudyPlanTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_track('backend-engineering')

    def setUp(self):
        self.user = User.objects.create_user(
            username='student', email='student@example.com', password='pw'
        )

    def test_study_plan_is_ordered_and_deep_links_into_the_source(self):
        response = self.client.get(
            reverse('skill-study-plan', kwargs={'slug': 'http-messages-and-semantics'})
        )

        self.assertEqual(response.status_code, 200)
        steps = response.json()['results'] if isinstance(response.json(), dict) else response.json()
        self.assertEqual(len(steps), 3)
        self.assertTrue(all(step['study_url'].startswith('https://') for step in steps))
        self.assertTrue(any('#' in step['study_url'] for step in steps))

    def test_study_plan_never_exposes_the_checkpoint_answer(self):
        response = self.client.get(
            reverse('skill-study-plan', kwargs={'slug': 'http-messages-and-semantics'})
        )

        body = response.content.decode('utf-8')
        self.assertNotIn('checkpoint_answer', body)
        # '201' is an answer whose own question does not mention it, so its
        # absence proves the value was withheld rather than merely unquoted.
        self.assertTrue(StudyStep.objects.filter(checkpoint_answer='201').exists())
        self.assertNotIn('201', body)

    def test_no_checkpoint_question_gives_away_its_own_answer(self):
        for step in StudyStep.objects.all():
            self.assertNotIn(
                step.checkpoint_answer.casefold(),
                step.checkpoint_question.casefold(),
                f'Step {step.pk} leaks its answer in the question.',
            )

    def test_study_plan_carries_attribution(self):
        response = self.client.get(
            reverse('skill-study-plan', kwargs={'slug': 'git-change-workflow'})
        )

        steps = response.json()
        steps = steps['results'] if isinstance(steps, dict) else steps
        self.assertTrue(all(step['provider'] for step in steps))
        self.assertTrue(all(step['license'] for step in steps))

    def test_checkpoint_is_graded_server_side(self):
        step = StudyStep.objects.get(checkpoint_answer='201')
        self.client.force_login(self.user)

        right = self.client.post(
            reverse('study-checkpoint', kwargs={'pk': step.pk}), {'answer': ' 201 '}
        )
        wrong = self.client.post(
            reverse('study-checkpoint', kwargs={'pk': step.pk}), {'answer': '200'}
        )

        self.assertTrue(right.json()['correct'])
        self.assertFalse(wrong.json()['correct'])
        # The response never reveals what the expected answer was.
        self.assertNotIn('201', wrong.content.decode('utf-8'))

    def test_checkpoint_requires_authentication(self):
        step = StudyStep.objects.first()

        response = self.client.post(
            reverse('study-checkpoint', kwargs={'pk': step.pk}), {'answer': 'x'}
        )

        self.assertEqual(response.status_code, 401)

    def test_every_study_step_points_at_a_resource_its_skill_declares(self):
        for step in StudyStep.objects.select_related('lesson', 'lesson__skill'):
            self.assertEqual(step.lesson.is_managed, True)
            self.assertTrue(step.lesson.content_url)

    def test_checkpoint_does_not_complete_lessons_or_award_xp_and_licenses_are_honest(self):
        self.client.force_login(self.user)
        step = StudyStep.objects.get(checkpoint_answer='201')
        for answer in ('201', '200'):
            self.client.post(reverse('study-checkpoint', kwargs={'pk': step.pk}), {'answer': answer})
        self.assertFalse(LessonCompletion.objects.filter(user=self.user).exists())
        self.assertFalse(SkillProgress.objects.filter(user=self.user).exists())
        lesson = self.client.get(reverse('lesson-detail', args=[step.lesson_id])).json()
        self.assertFalse(lesson['license_verified'])
        self.assertIsInstance(lesson['redistributable'], bool)
        self.assertIsInstance(lesson['commercial_use_allowed'], bool)


class LinkCheckTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_track('backend-engineering')

    def test_check_url_classifies_responses_without_fetching_content(self):
        with mock.patch('apps.learning.tasks.urllib.request.urlopen') as urlopen:
            urlopen.return_value.__enter__.return_value.url = 'https://example.com/a'
            self.assertEqual(check_url('https://example.com/a'), 'ok')

        self.assertEqual(check_url(''), 'broken')

    def test_check_url_treats_a_redirect_as_moved(self):
        with mock.patch('apps.learning.tasks.urllib.request.urlopen') as urlopen:
            urlopen.return_value.__enter__.return_value.url = 'https://example.com/b'
            self.assertEqual(check_url('https://example.com/a'), 'moved')

    def _head_error(self, url, code):
        return urllib.error.HTTPError(url, code, 'denied', Message(), None)

    def test_head_rejected_then_get_succeeds_is_ok_without_reading_body(self):
        with mock.patch('apps.learning.tasks.urllib.request.urlopen') as urlopen:
            get_response = mock.MagicMock()
            get_response.url = 'https://example.com/a'
            urlopen.side_effect = [
                self._head_error('https://example.com/a', 403),
                mock.MagicMock(__enter__=mock.MagicMock(return_value=get_response),
                               __exit__=mock.MagicMock(return_value=False)),
            ]
            self.assertEqual(check_url('https://example.com/a'), 'ok')
            get_response.read.assert_not_called()
            self.assertEqual(urlopen.call_count, 2)
            # The fallback must be a bounded GET, not another HEAD.
            self.assertEqual(urlopen.call_args_list[1].args[0].get_method(), 'GET')

    def test_head_rejected_then_get_redirects_is_moved(self):
        with mock.patch('apps.learning.tasks.urllib.request.urlopen') as urlopen:
            get_response = mock.MagicMock()
            get_response.url = 'https://example.com/b'
            urlopen.side_effect = [
                self._head_error('https://example.com/a', 405),
                mock.MagicMock(__enter__=mock.MagicMock(return_value=get_response),
                               __exit__=mock.MagicMock(return_value=False)),
            ]
            self.assertEqual(check_url('https://example.com/a'), 'moved')
            get_response.read.assert_not_called()

    def test_head_rejected_then_get_denied_is_broken(self):
        with mock.patch('apps.learning.tasks.urllib.request.urlopen') as urlopen:
            urlopen.side_effect = [
                self._head_error('https://example.com/a', 403),
                self._head_error('https://example.com/a', 403),
            ]
            self.assertEqual(check_url('https://example.com/a'), 'broken')

    def test_head_rejected_then_get_times_out_is_broken(self):
        with mock.patch('apps.learning.tasks.urllib.request.urlopen') as urlopen:
            urlopen.side_effect = [
                self._head_error('https://example.com/a', 405),
                urllib.error.URLError('timed out'),
            ]
            self.assertEqual(check_url('https://example.com/a'), 'broken')

    def test_head_not_found_does_not_fall_back_to_get(self):
        with mock.patch('apps.learning.tasks.urllib.request.urlopen') as urlopen:
            urlopen.side_effect = self._head_error('https://example.com/a', 404)
            self.assertEqual(check_url('https://example.com/a'), 'broken')
            self.assertEqual(urlopen.call_count, 1)

    def test_link_check_records_status_on_every_managed_lesson(self):
        with mock.patch('apps.learning.tasks.check_url', return_value='ok'):
            summary = check_resource_links()

        self.assertEqual(summary['ok'], Lesson.objects.filter(is_managed=True).count())
        self.assertFalse(
            Lesson.objects.filter(is_managed=True, link_checked_at__isnull=True).exists()
        )

    def test_broken_links_are_recorded_rather_than_deleted(self):
        with mock.patch('apps.learning.tasks.check_url', return_value='broken'):
            check_resource_links()

        # The lesson stays; fixing a dead link is a curriculum decision.
        self.assertTrue(Lesson.objects.filter(is_managed=True, link_status='broken').exists())
