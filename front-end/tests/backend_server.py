"""Disposable Django backend for browser auth checks; no project DB writes.

Run from the repo root with backend dependencies: python front-end/tests/backend_server.py
"""
import io
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
    call_command('migrate', verbosity=0, stdout=io.StringIO())
    with make_server('127.0.0.1', 8011, get_wsgi_application()) as server:
        print('Disposable auth backend: http://127.0.0.1:8011 (in-memory DB)', flush=True)
        server.serve_forever()
