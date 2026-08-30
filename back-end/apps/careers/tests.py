from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from .models import CareerTrack


class CareerTrackModelTests(TestCase):
    """Tests for CareerTrack model."""

    def test_create_career_track(self):
        track = CareerTrack.objects.create(
            title='Backend Engineering',
            slug='backend-engineering',
            description='Learn backend development.',
        )
        self.assertEqual(str(track), 'Backend Engineering')
        self.assertTrue(track.is_active)
        self.assertIsNotNone(track.created_at)

    def test_slug_unique(self):
        """Slug should be unique."""
        CareerTrack.objects.create(title='Track A', slug='track-a')
        with self.assertRaises(Exception):
            CareerTrack.objects.create(title='Track B', slug='track-a')


class CareerTrackAPITests(TestCase):
    """Tests for CareerTrack API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.track = CareerTrack.objects.create(
            title='Backend Engineering',
            slug='backend-engineering',
            description='Backend development pathway.',
        )
        CareerTrack.objects.create(
            title='Inactive Track',
            slug='inactive-track',
            is_active=False,
        )

    def test_list_career_tracks(self):
        """List should return only active career tracks."""
        url = reverse('career-track-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only active tracks returned
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Backend Engineering')

    def test_detail_career_track(self):
        """Detail should return specific career track data."""
        url = reverse('career-track-detail', args=[self.track.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Backend Engineering')
        self.assertIn('competency_count', response.data)

    def test_detail_not_found(self):
        """Non-existent ID should return 404."""
        url = reverse('career-track-detail', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
