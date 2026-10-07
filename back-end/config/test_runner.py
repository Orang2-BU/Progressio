"""Test runner that keeps request budgets local, isolated, and clock-free."""
from django.core.cache import caches
from django.test import SimpleTestCase
from django.test.runner import DiscoverRunner
from django.test.utils import override_settings

# Local-memory caches keep the suite off Redis even when a developer `.env`
# points THROTTLE_CACHE_URL or CELERY_BROKER_URL at a real server.
TEST_CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'progressio-test-default',
    },
    'throttle': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'progressio-test-throttle',
    },
}

_django_pre_setup = SimpleTestCase._pre_setup


def _pre_setup_with_fresh_budget(test_case):
    """Django never clears caches between tests; budget counters must be reset.

    Without this a request made by one test would throttle an unrelated test in
    the same process, because locmem counters outlive the per-test database.
    """
    _django_pre_setup(test_case)
    caches['throttle'].clear()


class ProgressioTestRunner(DiscoverRunner):
    """Force the throttle cache onto memory and reset it before every test."""

    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        self._budget_settings = override_settings(
            CACHES=TEST_CACHES, THROTTLE_CACHE_ALIAS='throttle'
        )
        self._budget_settings.enable()
        setattr(SimpleTestCase, '_pre_setup', _pre_setup_with_fresh_budget)

    def tearDown_test_environment(self, **kwargs):
        setattr(SimpleTestCase, '_pre_setup', _django_pre_setup)
        self._budget_settings.disable()
        getattr(super(), 'tearDown_test_environment')(**kwargs)
