"""Disposable Django backend for browser checks; no project DB writes.

Run from the repo root with backend dependencies: python front-end/tests/backend_server.py
"""
import io
import argparse
import os
from pathlib import Path
import sys
from wsgiref.simple_server import make_server

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'back-end'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['DB_ENGINE'] = 'sqlite'

import django
from django.conf import settings

settings.DATABASES['default']['NAME'] = ':memory:'
settings.ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
settings.DEBUG = False
django.setup()

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--catalog', action='store_true', help='Import repo curriculum with small pages and empty/inactive fixtures.')
    args = parser.parse_args()
    call_command('migrate', verbosity=0, stdout=io.StringIO())
    if args.catalog:
        settings.REST_FRAMEWORK['PAGE_SIZE'] = 2
        call_command('seed_demo', stdout=io.StringIO())
        from apps.careers.models import CareerTrack
        CareerTrack.objects.create(title='Empty catalog fixture', slug='empty-fixture')
        CareerTrack.objects.create(title='Inactive fixture', slug='inactive-fixture', is_active=False)
        CareerTrack.objects.create(title='Pagination fixture', slug='pagination-fixture')
    with make_server('127.0.0.1', 8011, get_wsgi_application()) as server:
        print('Disposable backend: http://127.0.0.1:8011 (in-memory DB)', flush=True)
        server.serve_forever()
