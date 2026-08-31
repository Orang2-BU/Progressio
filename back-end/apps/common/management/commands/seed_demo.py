from django.core.management.base import BaseCommand
from django.db import transaction

from apps.assessments.models import Assessment, DiagnosticQuestion
from apps.careers.models import CareerTrack
from apps.competencies.models import Competency
from apps.learning.models import Lesson
from apps.skills.models import Skill, SkillPrerequisite


class Command(BaseCommand):
    help = 'Idempotently seed the Backend Engineering hackathon demo curriculum.'

    @transaction.atomic
    def handle(self, *args, **options):
        track, _ = CareerTrack.objects.update_or_create(
            slug='backend-engineering',
            defaults={
                'title': 'Backend Engineering',
                'description': 'Build secure, tested REST APIs with modern authentication.',
                'is_active': True,
            },
        )
        foundations, _ = Competency.objects.update_or_create(
            slug='backend-foundations',
            defaults={
                'career_track': track,
                'title': 'Backend Foundations',
                'description': 'HTTP, REST API design, and automated API testing.',
                'order': 1,
            },
        )
        authentication, _ = Competency.objects.update_or_create(
            slug='backend-authentication',
            defaults={
                'career_track': track,
                'title': 'Backend Authentication',
                'description': 'JWT authentication and role-based access control.',
                'order': 2,
            },
        )

        skills = {}
        skill_data = [
            (foundations, 'rest-api', 'REST API', 'beginner', 90),
            (foundations, 'api-testing', 'API Testing', 'intermediate', 120),
            (authentication, 'jwt-authentication', 'JWT Authentication', 'intermediate', 120),
            (authentication, 'role-based-access-control', 'Role-Based Access Control', 'intermediate', 90),
        ]
        for competency, slug, title, difficulty, minutes in skill_data:
            skill, _ = Skill.objects.update_or_create(
                slug=slug,
                defaults={
                    'competency': competency,
                    'title': title,
                    'difficulty': difficulty,
                    'estimated_learning_minutes': minutes,
                },
            )
            skills[slug] = skill

        prerequisites = [
            ('api-testing', 'rest-api'),
            ('jwt-authentication', 'rest-api'),
            ('role-based-access-control', 'jwt-authentication'),
        ]
        for skill_slug, required_slug in prerequisites:
            SkillPrerequisite.objects.get_or_create(
                skill=skills[skill_slug],
                required_skill=skills[required_slug],
            )

        for index, (slug, title) in enumerate([
            ('rest-api', 'Designing Resource-Oriented REST APIs'),
            ('api-testing', 'Testing API Contracts and Error Cases'),
            ('jwt-authentication', 'JWT Authentication Fundamentals'),
            ('role-based-access-control', 'Implementing RBAC Safely'),
        ], start=1):
            Lesson.objects.update_or_create(
                skill=skills[slug],
                order=1,
                defaults={
                    'title': title,
                    'content_type': Lesson.ContentType.ARTICLE,
                    'duration': 20 + index * 5,
                    'content_url': '',
                },
            )

        questions = [
            ('rest-api', 'Which HTTP method is normally idempotent?', ['POST', 'PUT'], 'PUT'),
            ('rest-api', 'Which status code means a resource was created?', ['200', '201'], '201'),
            ('api-testing', 'What should an authorization test include?', ['Only success cases', 'Forbidden cases'], 'Forbidden cases'),
            ('api-testing', 'Which assertion verifies an unauthorized request?', ['Status 401', 'Status 201'], 'Status 401'),
            ('jwt-authentication', 'Where is a bearer token normally sent?', ['Authorization header', 'CSS file'], 'Authorization header'),
            ('jwt-authentication', 'What must a JWT verifier validate?', ['Signature and claims', 'File extension'], 'Signature and claims'),
            ('role-based-access-control', 'What should determine resource access?', ['Verified permissions', 'UI visibility'], 'Verified permissions'),
            ('role-based-access-control', 'Where must RBAC be enforced?', ['Server side', 'Client side only'], 'Server side'),
        ]
        for order, (skill_slug, prompt, choices, correct_answer) in enumerate(questions, start=1):
            DiagnosticQuestion.objects.update_or_create(
                career_track=track,
                prompt=prompt,
                defaults={
                    'skill': skills[skill_slug],
                    'options': [{'value': choice, 'label': choice} for choice in choices],
                    'correct_answer': correct_answer,
                    'order': order,
                    'is_active': True,
                },
            )

        Assessment.objects.update_or_create(
            skill=skills['role-based-access-control'],
            title='Build a Secure JWT + RBAC API',
            defaults={
                'assessment_type': Assessment.AssessmentType.CHALLENGE,
                'instructions': (
                    'Submit relevant source code, automated test output, and a short README. '
                    'The API must authenticate JWTs and enforce at least two roles server-side.'
                ),
                'passing_score': 70,
                'max_score': 100,
                'evaluation_mode': Assessment.EvaluationMode.AI,
                'grading_config': {
                    'rubric': [
                        {'criterion': 'Authentication', 'weight': 30},
                        {'criterion': 'Authorization/RBAC', 'weight': 30},
                        {'criterion': 'Automated tests', 'weight': 25},
                        {'criterion': 'Code quality and documentation', 'weight': 15},
                    ]
                },
            },
        )

        self.stdout.write(self.style.SUCCESS(
            'Demo curriculum ready: 1 track, 2 competencies, 4 skills, '
            '4 lessons, 8 diagnostic questions, and 1 coding challenge.'
        ))
