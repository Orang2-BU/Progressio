from typing import cast

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.response import Response as APIResponse
from rest_framework import status

from apps.common.testing import frozen_budget_clock, throttle_key
from apps.common.throttling import (
    AuthLoginThrottle,
    AuthRefreshThrottle,
    AuthRegisterThrottle,
)

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

    def test_public_registration_cannot_create_admin(self):
        data = {
            'username': 'attacker',
            'email': 'attacker@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'role': 'admin',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='attacker').exists())


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


def budgeted(**overrides):
    """Replace one or more documented budgets for a single test."""
    return override_settings(
        THROTTLE_RATES={**settings.THROTTLE_RATES, **overrides}
    )


class AuthBudgetTests(TestCase):
    """Credential endpoints spend a bounded budget and report the wait."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='budgetuser', email='budget@example.com', password='SecurePass123!'
        )
        self.neighbour = User.objects.create_user(
            username='neighbour', email='neighbour@example.com', password='SecurePass123!'
        )
        self.login_url = reverse('auth-login')
        self.refresh_url = reverse('auth-refresh')
        self.register_url = reverse('auth-register')

    def login(self, username='budgetuser', password='SecurePass123!', **environ) -> APIResponse:
        return cast(APIResponse, self.client.post(
            self.login_url,
            {'username': username, 'password': password},
            format='json',
            **environ,
        ))

    def register(self, username, **environ) -> APIResponse:
        return cast(APIResponse, self.client.post(
            self.register_url,
            {
                'username': username,
                'email': f'{username}@example.com',
                'password': 'SecurePass123!',
                'password_confirm': 'SecurePass123!',
            },
            format='json',
            **environ,
        ))

    def refresh(self, token) -> APIResponse:
        return cast(
            APIResponse,
            self.client.post(self.refresh_url, {'refresh': token}, format='json'),
        )

    def assert_retry_information(self, response):
        """429 carries one wait value, in the header and in the body."""
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        seconds = response.data['retry_after_seconds']
        self.assertIsInstance(seconds, int)
        self.assertGreater(seconds, 0)
        self.assertEqual(response['Retry-After'], str(seconds))
        self.assertIn(str(seconds), response.data['detail'])

    @budgeted(auth_login='2/min')
    def test_login_over_budget_returns_429_with_consistent_retry_information(self):
        self.assertEqual(self.login().status_code, status.HTTP_200_OK)
        self.assertEqual(self.login().status_code, status.HTTP_200_OK)
        self.assert_retry_information(self.login())

    @budgeted(auth_login='10/min')
    def test_documented_login_budget_allows_a_normal_sign_in_burst(self):
        """The shipped value is the one the operator documentation promises."""
        for _ in range(10):
            self.assertEqual(self.login().status_code, status.HTTP_200_OK)
        self.assert_retry_information(self.login())

    @budgeted(auth_login='1/min')
    def test_login_budget_recovers_once_the_window_has_passed(self):
        with frozen_budget_clock() as clock:
            self.assertEqual(self.login().status_code, status.HTTP_200_OK)
            blocked = self.login()
            # One request per minute, so the wait is the whole window.
            self.assert_retry_information(blocked)
            self.assertEqual(int(blocked['Retry-After']), 60)
            clock.advance(59)
            self.assert_retry_information(self.login())
            clock.advance(2)
            self.assertEqual(self.login().status_code, status.HTTP_200_OK)

    @budgeted(auth_login='1/min')
    def test_login_budget_is_isolated_per_account(self):
        """One account exhausting its budget must not lock out its neighbour."""
        self.assertEqual(self.login().status_code, status.HTTP_200_OK)
        self.assert_retry_information(self.login())
        self.assertEqual(
            self.login(username='neighbour').status_code, status.HTTP_200_OK
        )

    @budgeted(auth_login_ip='1/min')
    def test_login_budget_also_caps_many_account_guesses_from_one_address(self):
        self.assertEqual(self.login().status_code, status.HTTP_200_OK)
        self.assert_retry_information(self.login(username='neighbour'))

    @budgeted(auth_register='1/hour')
    def test_register_budget_is_counted_per_address(self):
        self.assertEqual(self.register('first').status_code, status.HTTP_201_CREATED)
        self.assert_retry_information(self.register('second'))
        # A different address is a different budget, so sign-up still works.
        self.assertEqual(
            self.register('third', REMOTE_ADDR='203.0.113.9').status_code,
            status.HTTP_201_CREATED,
        )

    @budgeted(auth_refresh='1/min')
    def test_refresh_budget_is_counted_per_address(self):
        token = self.login().data['refresh']
        self.assertEqual(self.refresh(token).status_code, status.HTTP_200_OK)
        self.assert_retry_information(self.refresh(token))

    @budgeted(auth_login='1/min')
    def test_budget_keys_never_carry_a_password_token_or_account_name(self):
        """A cache dump must not hand over credentials or list account names."""
        refresh_token = self.login().data['refresh']
        login_key = throttle_key(
            AuthLoginThrottle,
            data={'username': 'budgetuser', 'password': 'SecurePass123!'},
        )
        self.assertNotIn('SecurePass123!', login_key)
        self.assertNotIn('budgetuser', login_key)
        refresh_key = throttle_key(
            AuthRefreshThrottle, data={'refresh': refresh_token}
        )
        self.assertNotIn(refresh_token, refresh_key)
        register_key = throttle_key(
            AuthRegisterThrottle,
            data={'username': 'budgetuser', 'password': 'SecurePass123!'},
        )
        self.assertNotIn('SecurePass123!', register_key)
        self.assertNotIn('budgetuser', register_key)

    @budgeted(auth_register='1/hour')
    def test_forwarded_header_cannot_mint_a_new_budget_by_default(self):
        """With no proxy configured the header is ignored, so it cannot be spoofed."""
        self.assertEqual(self.register('first').status_code, status.HTTP_201_CREATED)
        self.assert_retry_information(
            self.register('second', HTTP_X_FORWARDED_FOR='203.0.113.7')
        )
        self.assert_retry_information(
            self.register('third', HTTP_X_FORWARDED_FOR='198.51.100.4')
        )

    @budgeted(auth_register='1/hour')
    @override_settings(TRUSTED_PROXY_COUNT=1)
    def test_forwarded_header_is_used_behind_a_configured_proxy(self):
        """The client address comes from the chain the operator declared."""
        self.assertEqual(
            self.register('first', REMOTE_ADDR='10.0.0.1',
                          HTTP_X_FORWARDED_FOR='203.0.113.7').status_code,
            status.HTTP_201_CREATED,
        )
        self.assert_retry_information(
            self.register('second', REMOTE_ADDR='10.0.0.1',
                          HTTP_X_FORWARDED_FOR='203.0.113.7')
        )
        # A different client behind the same proxy keeps its own budget.
        self.assertEqual(
            self.register('third', REMOTE_ADDR='10.0.0.1',
                          HTTP_X_FORWARDED_FOR='198.51.100.4').status_code,
            status.HTTP_201_CREATED,
        )

    @budgeted(auth_register='1/hour')
    @override_settings(TRUSTED_PROXY_COUNT=2)
    def test_forged_forwarded_header_is_refused_behind_two_proxies(self):
        """A header shorter than the declared chain is not believed at all."""
        self.assertEqual(
            self.register('first', REMOTE_ADDR='10.0.0.1',
                          HTTP_X_FORWARDED_FOR='9.9.9.9').status_code,
            status.HTTP_201_CREATED,
        )
        self.assert_retry_information(
            self.register('second', REMOTE_ADDR='10.0.0.1',
                          HTTP_X_FORWARDED_FOR='8.8.8.8')
        )
