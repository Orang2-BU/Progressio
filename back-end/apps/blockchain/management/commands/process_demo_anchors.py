import time
from django.core.management.base import BaseCommand
from apps.blockchain.demo_anchor import DemoAnchorError, process_demo_anchor
from apps.blockchain.models import DemoAnchor


class Command(BaseCommand):
    help = 'Submit/reconcile queued Base Sepolia demo digest transactions.'

    def add_arguments(self, parser):
        parser.add_argument('--loop', action='store_true')
        parser.add_argument('--interval', type=int, default=8)

    def handle(self, *args, **options):
        while True:
            ids = list(DemoAnchor.objects.filter(state__in=[DemoAnchor.State.QUEUED,
                DemoAnchor.State.SUBMITTED]).order_by('created_at').values_list('pk', flat=True)[:25])
            for anchor_id in ids:
                try:
                    anchor = process_demo_anchor(anchor_id)
                    self.stdout.write(f'{anchor_id}: {anchor.state}')
                except DemoAnchorError as exc:
                    # Error identifiers are intentionally fixed/sanitized; never log RPC responses or secrets.
                    self.stderr.write(f'{anchor_id}: retryable {exc}')
                except Exception:
                    self.stderr.write(f'{anchor_id}: retryable worker_error')
            if not options['loop']:
                return
            time.sleep(max(2, min(60, options['interval'])))
