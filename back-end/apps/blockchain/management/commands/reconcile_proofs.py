from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from apps.blockchain.models import ProofDelivery
from apps.blockchain.services import BlockchainService


class Command(BaseCommand):
    help = 'Deliver ready proofs and reconcile uncertain proofs using their existing identities.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100)

    def handle(self, *args, **options):
        deliveries = ProofDelivery.objects.filter(
            state__in=[ProofDelivery.State.READY, ProofDelivery.State.UNKNOWN, ProofDelivery.State.SENDING],
            credential__status='pending',
        ).filter(Q(lease_until__isnull=True) | Q(lease_until__lte=timezone.now())).order_by('created_at')
        for delivery in deliveries[:max(0, options['limit'])]:
            BlockchainService.record_credential_on_chain(delivery.credential)
            delivery.refresh_from_db()
            self.stdout.write(f'{delivery.credential_id}: {delivery.state} {delivery.error_code}')
