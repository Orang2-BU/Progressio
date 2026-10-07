from celery import shared_task
from apps.credentials.models import Credential
from .services import BlockchainService


@shared_task(name="apps.blockchain.tasks.publish_credential_to_blockchain_task")
def publish_credential_to_blockchain_task(credential_id):
    """
    Deliver or reconcile the same durable proof record; duplicate tasks are safe.
    """
    try:
        credential = Credential.objects.select_related(
            'competency', 'competency__career_track', 'user'
        ).get(id=credential_id)

        proof = BlockchainService.record_credential_on_chain(credential)
        if proof is None:
            return f"Credential {credential_id} proof remains unconfirmed; inspect its durable delivery record."
        return f"Credential {credential_id} successfully anchored on Blockchain [{proof.network}]. Tx: {proof.transaction_hash}"
    except Credential.DoesNotExist:
        return f"Credential {credential_id} not found"
    except Exception:
        return f"Credential {credential_id} proof outcome is unknown; reconcile the existing delivery."
