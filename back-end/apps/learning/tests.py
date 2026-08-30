from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.careers.models import CareerTrack
from apps.competencies.models import Competency
from apps.skills.models import Skill
from .models import Lesson


class LessonModelTests(TestCase):

    def setUp(self):
        self.track = CareerTrack.objects.create(title='Backend', slug='backend')
        self.comp = Competency.objects.create(
            career_track=self.track, title='Foundations', slug='foundations', order=1
        )
        self.skill = Skill.objects.create(
            competency=self.comp, title='REST API', slug='rest-api',
            difficulty=Skill.Difficulty.BEGINNER, estimated_learning_minutes=60
        )

    def test_create_lesson(self):
        lesson = Lesson.objects.create(
            skill=self.skill,
            title='Intro to REST',
            content_type=Lesson.ContentType.VIDEO,
            content_url='https://example.com/video',
            duration=15,
            order=1
        )
        self.assertEqual(str(lesson), 'REST API - Intro to REST')
        self.assertEqual(lesson.skill, self.skill)


class LessonAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.track = CareerTrack.objects.create(title='Backend', slug='backend')
        self.comp = Competency.objects.create(
            career_track=self.track, title='Foundations', slug='foundations', order=1
        )
        self.skill1 = Skill.objects.create(
            competency=self.comp, title='REST API', slug='rest-api',
            difficulty=Skill.Difficulty.BEGINNER, estimated_learning_minutes=60
        )
        self.skill2 = Skill.objects.create(
            competency=self.comp, title='Authentication', slug='authentication',
            difficulty=Skill.Difficulty.INTERMEDIATE, estimated_learning_minutes=90
        )
        self.lesson1 = Lesson.objects.create(
            skill=self.skill1, title='Intro to REST',
            content_type=Lesson.ContentType.VIDEO, duration=15, order=1
        )
        self.lesson2 = Lesson.objects.create(
            skill=self.skill1, title='HTTP Methods',
            content_type=Lesson.ContentType.ARTICLE, duration=20, order=2
        )
        self.lesson3 = Lesson.objects.create(
            skill=self.skill2, title='JWT Basics',
            content_type=Lesson.ContentType.ARTICLE, duration=25, order=1
        )

    def test_list_lessons(self):
        url = reverse('lesson-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 3)

    def test_filter_lessons_by_skill(self):
        url = reverse('lesson-list')
        response = self.client.get(url, {'skill': self.skill1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)

    def test_detail_lesson(self):
        url = reverse('lesson-detail', args=[self.lesson1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Intro to REST')
        self.assertEqual(response.data['skill_title'], 'REST API')
