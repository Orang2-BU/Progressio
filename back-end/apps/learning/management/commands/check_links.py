from django.core.management.base import BaseCommand

from apps.learning.models import Lesson
from apps.learning.tasks import check_resource_links


class Command(BaseCommand):
    help = 'Check that every curriculum resource URL is still reachable.'

    def handle(self, *args, **options):
        summary = check_resource_links()
        self.stdout.write(
            f"ok={summary['ok']} moved={summary['moved']} broken={summary['broken']}"
        )
        for lesson in Lesson.objects.filter(is_managed=True).exclude(link_status='ok'):
            self.stdout.write(self.style.WARNING(
                f'  {lesson.link_status}: {lesson.source_id} -> {lesson.content_url}'
            ))
        if summary['broken']:
            self.stdout.write(self.style.ERROR(
                'Broken links must be fixed in the curriculum package, not in the database.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('All curriculum links reachable.'))
