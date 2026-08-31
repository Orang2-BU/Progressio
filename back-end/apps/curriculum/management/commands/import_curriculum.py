from django.core.management.base import BaseCommand, CommandError

from apps.curriculum.importer import import_track
from apps.curriculum.loader import CurriculumError, available_tracks


class Command(BaseCommand):
    help = (
        'Import validated curriculum packages from curriculum/tracks/ into the database. '
        'The package is the source of truth; the import is idempotent.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--track',
            action='append',
            dest='tracks',
            help='Track ID to import. Repeatable. Defaults to every track found.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report what would change without writing anything.',
        )
        parser.add_argument(
            '--prune',
            action='store_true',
            help=(
                'Delete managed records the package no longer declares. '
                'Refuses to run when learner data depends on them.'
            ),
        )

    def handle(self, *args, **options):
        tracks = options['tracks'] or available_tracks()
        if not tracks:
            raise CommandError('No curriculum packages found under curriculum/tracks/.')

        for track_id in tracks:
            self.stdout.write(f'Importing curriculum: {track_id}')
            try:
                report = import_track(
                    track_id,
                    dry_run=options['dry_run'],
                    prune=options['prune'],
                )
            except CurriculumError as error:
                raise CommandError(str(error)) from error

            for line in report.lines():
                self.stdout.write(line)
            if report.is_empty:
                self.stdout.write('  no changes')
            for note in report.skipped:
                self.stdout.write(self.style.NOTICE(f'  deferred: {note}'))
            for warning in report.warnings:
                self.stdout.write(self.style.WARNING(f'  warning: {warning}'))

        if options['dry_run']:
            self.stdout.write(self.style.NOTICE('Dry run - no changes were written.'))
        else:
            self.stdout.write(self.style.SUCCESS('Curriculum import complete.'))
