from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AuthRegistrationTests(TestCase):
    """Tests for user registration endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('auth-register')

    def test_register_success(self):
        """Valid registration should return 201 and user data."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'role': 'student'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['role'], 'student')
        self.assertNotIn('password', response.data)

    def test_register_password_mismatch(self):
        """Mismatched passwords should return 400."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'WrongPass456!',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        """Duplicate username should return 400."""
        User.objects.create_user(
            username='existing', email='a@b.com', password='Pass1234!'
        )
        data = {
            'username': 'existing',
            'email': 'new@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_email(self):
        """Missing email should return 400."""
        data = {
            'username': 'testuser',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthJWTTests(TestCase):
    """Tests for JWT login, refresh, and me endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='jwtuser',
            email='jwt@example.com',
            password='SecurePass123!',
            role='student'
        )
        self.login_url = reverse('auth-login')
        self.refresh_url = reverse('auth-refresh')
        self.me_url = reverse('auth-me')

    def test_login_success(self):
        """Valid credentials should return access and refresh tokens."""
        data = {'username': 'jwtuser', 'password': 'SecurePass123!'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_password(self):
        """Invalid password should return 401."""
        data = {'username': 'jwtuser', 'password': 'WrongPassword!'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        """Valid refresh token should return new access token."""
        login_response = self.client.post(
            self.login_url,
            {'username': 'jwtuser', 'password': 'SecurePass123!'},
            format='json'
        )
        refresh_token = login_response.data['refresh']
        response = self.client.post(
            self.refresh_url,
            {'refresh': refresh_token},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_me_authenticated(self):
        """Authenticated user should get their profile."""
        login_response = self.client.post(
            self.login_url,
            {'username': 'jwtuser', 'password': 'SecurePass123!'},
            format='json'
        )
        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'jwtuser')
        self.assertEqual(response.data['role'], 'student')

    def test_me_unauthenticated(self):
        """Unauthenticated request to /me should return 401."""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
