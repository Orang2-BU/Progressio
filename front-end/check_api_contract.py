"""Run with back-end/.venv/Scripts/python.exe front-end/check_api_contract.py.

Phase 0 API probe: uses an in-memory database and mock providers only.
Known contract gaps are reported, not silently treated as passing features.
"""
import io
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'back-end'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['DB_ENGINE'] = 'sqlite'
os.environ['AI_PROVIDER'] = 'mock'
os.environ['BLOCKCHAIN_PROVIDER'] = 'mock'

import django
from django.conf import settings

settings.DATABASES['default']['NAME'] = ':memory:'
settings.ALLOWED_HOSTS = ['testserver']
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APIClient
from apps.assessments.models import Assessment, DiagnosticQuestion
from apps.careers.models import CareerTrack
from apps.skills.models import Skill


def main():
    output = io.StringIO()
    call_command('migrate', verbosity=0, stdout=output)
    call_command('import_curriculum', stdout=output)
    schema_output = io.StringIO()
    call_command('spectacular', format='openapi-json', fail_on_warn=True,
                 stdout=schema_output)
    schema = json.loads(schema_output.getvalue())
    client = APIClient()
    user = get_user_model().objects.create_user(
        username='contract-probe', password='LocalProbe-4821!')
    track = CareerTrack.objects.get(slug='backend-engineering')
    skill = Skill.objects.get(slug='client-server-model')
    assessment = Assessment.objects.get(skill=skill, evaluation_mode='rules')
    checks = 0

    def request(method, path, status=200, data=None):
        nonlocal checks
        response = getattr(client, method)('/api/v1/' + path, data=data, format='json')
        assert response.status_code == status, (path, response.status_code, response.data)
        checks += 1
        return response.data

    request('get', 'progress', status=401)
    login = request('post', 'auth/login', data={
        'username': user.username, 'password': 'LocalProbe-4821!'})
    assert {'access', 'refresh'} <= login.keys()
    request('post', 'auth/refresh', data={'refresh': login['refresh']})
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + login['access'])
    request('get', 'auth/me')
    for path in ('career-tracks/', f'competencies/?career_track={track.pk}',
                 f'skills/?competency={skill.competency_id}',
                 f'assessments/?skill={skill.pk}', f'skills/{skill.slug}/study-plan',
                 f'lessons?skill={skill.pk}', 'credentials/'):
        assert {'count', 'next', 'previous', 'results'} <= request('get', path).keys()
    assert isinstance(request('get', f'diagnostics/{track.pk}'), list)
    assert isinstance(request('get', f'learning-path?career_track={track.slug}'), list)
    roadmap = request('get', f'roadmap?skill={skill.slug}')
    assert {'target', 'steps', 'already_satisfied', 'remaining_hours'} <= roadmap.keys()
    request('get', 'roadmap', status=400)
    detail = request('get', f'assessments/{assessment.pk}')
    assert 'questions' in detail and 'grading_config' not in detail
    request('post', f'assessments/{assessment.pk}/submit', status=400,
            data={'score': 100, 'content': {}})
    submission = request('post', f'assessments/{assessment.pk}/submit', status=201,
                         data={'content': {'answers': assessment.grading_config['answer_key']}})
    assert submission['status'] == 'completed' and submission['is_passed']
    answers = {str(q.pk): q.correct_answer for q in
               DiagnosticQuestion.objects.filter(career_track=track, is_active=True)}
    request('get', f'diagnostics/latest?career_track={track.pk}', status=404)
    request('post', f'diagnostics/{track.pk}/submit', status=201, data={'answers': answers})
    request('get', f'diagnostics/latest?career_track={track.pk}')
    second = request('post', f'diagnostics/{track.pk}/submit', status=201, data={'answers': answers})
    latest = request('get', f'diagnostics/latest?career_track={track.pk}')
    assert latest['id'] == second['id']
    print(f'PASS: {checks} API requests; OpenAPI generated without warnings.')
    print('PASS: latest diagnostic returns the second attempt.')
    operation = schema['paths']['/api/v1/study-steps/{id}/checkpoint']['post']
    print('SCHEMA GAP: checkpoint response has no content schema:',
          'content' not in operation['responses']['200'])
    parameters = schema['paths']['/api/v1/learning-path']['get'].get('parameters', [])
    print('SCHEMA GAP: learning-path career_track parameter missing:',
          not any(p['name'] == 'career_track' for p in parameters))


if __name__ == '__main__':
    main()
