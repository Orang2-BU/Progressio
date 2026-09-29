from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.careers.models import CareerTrack
from apps.competencies.models import Competency
from apps.skills.models import Skill, SkillPrerequisite
from .models import Lesson, LessonCompletion, SkillProgress, CompetencyProgress

User = get_user_model()


class LearningAndProgressTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='learner', email='learner@example.com', password='Password123!', role='student'
        )
        self.track = CareerTrack.objects.create(title='Backend', slug='backend')
        self.comp = Competency.objects.create(
            career_track=self.track, title='Foundations', slug='foundations', order=1
        )
        self.skill1 = Skill.objects.create(
            competency=self.comp, title='Python Basics', slug='python-basics',
            difficulty=Skill.Difficulty.BEGINNER, estimated_learning_minutes=60
        )
        self.skill2 = Skill.objects.create(
            competency=self.comp, title='Django Framework', slug='django-framework',
            difficulty=Skill.Difficulty.INTERMEDIATE, estimated_learning_minutes=120
        )
        # Prerequisite: Django requires Python Basics
        SkillPrerequisite.objects.create(skill=self.skill2, required_skill=self.skill1)

        self.lesson1 = Lesson.objects.create(
            skill=self.skill1, title='Variables and Types',
            content_type=Lesson.ContentType.VIDEO, duration=15, order=1
        )
        self.lesson2 = Lesson.objects.create(
            skill=self.skill1, title='Functions and Classes',
            content_type=Lesson.ContentType.ARTICLE, duration=20, order=2
        )

    def test_complete_lesson_awards_xp_and_mastery(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('lesson-complete', args=[self.lesson1.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        self.assertEqual(response.data['xp_earned'], 50)
        self.assertTrue(response.data['newly_completed'])
        self.assertEqual(response.data['current_skill_mastery'], 35.0)  # 1/2 lessons = 50% * 70 = 35%
        self.assertEqual(response.data['current_skill_xp'], 50)

        # Complete second lesson
        url2 = reverse('lesson-complete', args=[self.lesson2.id])
        response2 = self.client.post(url2)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['current_skill_mastery'], 70.0)  # 2/2 lessons = 100% * 70 = 70%
        self.assertEqual(response2.data['current_skill_xp'], 100)

        # Completing same lesson again should not award double XP
        response_dup = self.client.post(url2)
        self.assertEqual(response_dup.data['xp_earned'], 0)
        self.assertFalse(response_dup.data['newly_completed'])

    def test_user_progress_overview_endpoint(self):
        self.client.force_authenticate(user=self.user)
        # Complete one lesson
        reverse_url = reverse('lesson-complete', args=[self.lesson1.id])
        self.client.post(reverse_url)

        url = reverse('user-progress')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_xp'], 50)
        self.assertEqual(response.data['completed_lessons_count'], 1)
        self.assertEqual(response.data['completed_lesson_ids'], [self.lesson1.id])
        self.assertEqual(len(response.data['skills']), 1)
        self.assertEqual(len(response.data['competencies']), 1)

    def test_completion_ids_persist_and_are_isolated_without_diagnostic_inference(self):
        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.client.get(reverse('user-progress')).data['completed_lesson_ids'], [])
        SkillProgress.objects.create(user=self.user, skill=self.skill1, mastery=100, xp=0)
        self.assertEqual(self.client.get(reverse('user-progress')).data['completed_lesson_ids'], [])
        url = reverse('lesson-complete', args=[self.lesson1.id])
        self.client.post(url)
        self.client.post(url)
        result = self.client.get(reverse('user-progress')).data
        self.assertEqual(result['completed_lesson_ids'], [self.lesson1.id])
        self.assertEqual(result['total_xp'], 50)
        self.assertEqual(result['skills'][0]['mastery'], 100)
        other = User.objects.create_user(username='other-learner')
        self.client.force_authenticate(user=other)
        self.assertEqual(self.client.get(reverse('user-progress')).data['completed_lesson_ids'], [])
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get(reverse('user-progress')).status_code, 401)
        self.assertEqual(self.client.post(url).status_code, 401)

    def test_failed_reward_rolls_back_completion_and_progress(self):
        from unittest.mock import patch
        from .services import ProgressService
        with patch.object(ProgressService, 'recalculate_competency_progress', side_effect=RuntimeError('failed')):
            with self.assertRaises(RuntimeError):
                ProgressService.complete_lesson(self.user, self.lesson1)
        self.assertFalse(LessonCompletion.objects.filter(user=self.user).exists())
        self.assertFalse(SkillProgress.objects.filter(user=self.user).exists())

    def test_learning_path_graph_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('learning-path')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        nodes = response.data
        self.assertEqual(len(nodes), 2)

        # skill1 has no prerequisites -> status: available
        skill1_node = next(n for n in nodes if n['skill_id'] == self.skill1.id)
        self.assertEqual(skill1_node['status'], 'available')

        # skill2 requires skill1 with mastery >= 70 -> status: locked
        skill2_node = next(n for n in nodes if n['skill_id'] == self.skill2.id)
        self.assertEqual(skill2_node['status'], 'locked')
        self.assertEqual(len(skill2_node['missing_prerequisites']), 1)
        self.assertEqual(skill2_node['missing_prerequisites'][0]['id'], self.skill1.id)

        # Now complete both lessons of skill1 so mastery reaches 70%
        self.client.post(reverse('lesson-complete', args=[self.lesson1.id]))
        self.client.post(reverse('lesson-complete', args=[self.lesson2.id]))

        # Re-check learning path
        response_after = self.client.get(url)
        skill2_after = next(n for n in response_after.data if n['skill_id'] == self.skill2.id)
        # Prerequisite met -> skill2 is now available!
        self.assertEqual(skill2_after['status'], 'available')
        self.assertEqual(len(skill2_after['missing_prerequisites']), 0)
