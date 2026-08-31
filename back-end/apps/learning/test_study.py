from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.curriculum.importer import import_track

from .models import Lesson, StudyStep
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
