from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.careers.models import CareerTrack
from .models import Competency


class CompetencyModelTests(TestCase):

    def setUp(self):
        self.track = CareerTrack.objects.create(
            title='Backend Engineering', slug='backend-engineering'
        )

    def test_create_competency(self):
        comp = Competency.objects.create(
            career_track=self.track,
            title='Programming Fundamentals',
            slug='programming-fundamentals',
            order=1
        )
        self.assertEqual(str(comp), 'Programming Fundamentals')
        self.assertEqual(comp.career_track, self.track)

    def test_slug_unique(self):
        Competency.objects.create(
            career_track=self.track, title='A', slug='comp-a', order=1
        )
        with self.assertRaises(Exception):
            Competency.objects.create(
                career_track=self.track, title='B', slug='comp-a', order=2
            )


class CompetencyAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.track = CareerTrack.objects.create(
            title='Backend Engineering', slug='backend-engineering'
        )
        self.track2 = CareerTrack.objects.create(
            title='Data Science', slug='data-science'
        )
        self.comp = Competency.objects.create(
            career_track=self.track,
            title='Programming Fundamentals',
            slug='programming-fundamentals',
            order=1
        )
        Competency.objects.create(
            career_track=self.track2,
            title='Statistics',
            slug='statistics',
            order=1
        )

    def test_list_all_competencies(self):
        url = reverse('competency-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)

    def test_filter_by_career_track(self):
        url = reverse('competency-list')
        response = self.client.get(url, {'career_track': self.track.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Programming Fundamentals')

    def test_detail_competency(self):
        url = reverse('competency-detail', args=[self.comp.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Programming Fundamentals')
        self.assertIn('skill_count', response.data)
