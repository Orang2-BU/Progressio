from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.careers.models import CareerTrack
from apps.competencies.models import Competency
from apps.skills.models import Skill, SkillPrerequisite
from apps.learning.models import Lesson


class SkillModelTests(TestCase):

    def setUp(self):
        self.track = CareerTrack.objects.create(title='Backend', slug='backend')
        self.comp = Competency.objects.create(
            career_track=self.track, title='Foundations', slug='foundations', order=1
        )

    def test_create_skill(self):
        skill = Skill.objects.create(
            competency=self.comp,
            title='Docker',
            slug='docker',
            difficulty=Skill.Difficulty.INTERMEDIATE,
            estimated_learning_minutes=120
        )
        self.assertEqual(str(skill), 'Docker')
        self.assertEqual(skill.difficulty, 'intermediate')

    def test_skill_prerequisite(self):
        skill1 = Skill.objects.create(
            competency=self.comp, title='REST API', slug='rest-api'
        )
        skill2 = Skill.objects.create(
            competency=self.comp, title='JWT Auth', slug='jwt-auth'
        )
        prereq = SkillPrerequisite.objects.create(skill=skill2, required_skill=skill1)
        self.assertEqual(str(prereq), 'JWT Auth requires REST API')


class SkillAPITests(TestCase):

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
        SkillPrerequisite.objects.create(skill=self.skill2, required_skill=self.skill1)
        self.lesson = Lesson.objects.create(
            skill=self.skill1, title='Intro Lesson',
            content_type=Lesson.ContentType.ARTICLE, duration=10, order=1
        )

    def test_list_skills(self):
        url = reverse('skill-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)

    def test_filter_skills_by_competency(self):
        url = reverse('skill-list')
        response = self.client.get(url, {'competency': self.comp.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)

    def test_detail_skill_with_prerequisites(self):
        url = reverse('skill-detail', args=[self.skill2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Authentication')
        self.assertEqual(len(response.data['prerequisites']), 1)
        self.assertEqual(
            response.data['prerequisites'][0]['required_skill_title'],
            'REST API'
        )

    def test_skill_lessons_endpoint(self):
        url = reverse('skill-lessons', args=[self.skill1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Intro Lesson')
