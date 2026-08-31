from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.curriculum.importer import import_track
from apps.curriculum.loader import CurriculumError, available_tracks

User = get_user_model()

DEMO_USERS = [
    ('student', 'student@progressio.demo', 'student'),
    ('recruiter', 'recruiter@progressio.demo', 'recruiter'),
]
DEMO_PASSWORD = 'progressio-demo-2026'


class Command(BaseCommand):
    help = (
        'Prepare a demo environment: import every curriculum package, then add '
        'demo accounts. The curriculum itself is never defined here — it comes '
        'from tracks/, which is the source of truth.'
    )

    @transaction.atomic
    def handle(self, *args, **options):
        tracks = available_tracks()
        if not tracks:
            self.stdout.write(self.style.WARNING('No curriculum packages found under tracks/.'))

        for track_id in tracks:
            try:
                report = import_track(track_id)
            except CurriculumError as error:
                self.stdout.write(self.style.ERROR(f'{track_id}: {error}'))
                continue
            created = sum(report.created.values())
            updated = sum(report.updated.values())
            self.stdout.write(f'{track_id}: {created} created, {updated} updated')
            for warning in report.warnings:
                self.stdout.write(self.style.WARNING(f'  warning: {warning}'))

        for username, email, role in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'role': role},
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save(update_fields=['password'])

        self.stdout.write(self.style.SUCCESS(
            f'Demo ready: {len(tracks)} track(s) imported, '
            f'{len(DEMO_USERS)} demo accounts available.'
        ))
