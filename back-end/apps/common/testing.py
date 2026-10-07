"""Test helpers for the request budgets in :mod:`apps.common.throttling`."""
from contextlib import contextmanager

from django.conf import settings
from django.core.cache import caches
from rest_framework.request import Request as DRFRequest
from rest_framework.test import APIRequestFactory

from . import throttling


class BudgetClock:
    """A hand-wound clock, so window expiry needs no sleeping."""

    def __init__(self, start=1_700_000_000.0):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@contextmanager
def frozen_budget_clock(start=1_700_000_000.0):
    """Drive the throttle clock from the test instead of from the wall clock."""
    clock = BudgetClock(start)
    original = throttling.now
    throttling.now = clock
    try:
        yield clock
    finally:
        throttling.now = original


def throttle_cache(alias=None):
    """The cache the throttles read, i.e. the one under test."""
    return caches[alias or settings.THROTTLE_CACHE_ALIAS]


def reset_budget(alias=None):
    """Drop every counter, as the test runner does between tests."""
    throttle_cache(alias).clear()


def throttle_key(throttle_class, method='post', path='/', data=None, **environ):
    """The cache key a throttle would use for a synthetic request.

    Lets a test assert on the identity a throttle builds without reaching into
    the cache backend's internals.
    """
    django_request = getattr(APIRequestFactory(), method)(path, data or {}, **environ)
    return throttle_class().get_cache_key(DRFRequest(django_request), None)


def client_address(throttle_class, method='post', path='/', data=None, **environ):
    """The address a throttle would attribute a synthetic request to."""
    django_request = getattr(APIRequestFactory(), method)(path, data or {}, **environ)
    return throttling.client_address(DRFRequest(django_request))