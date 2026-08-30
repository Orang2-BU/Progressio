from celery import shared_task
from apps.credentials.models import Credential
from .services import BlockchainService


@shared_task(name="apps.blockchain.tasks.publish_credential_to_blockchain_task")
def publish_credential_to_blockchain_task(credential_id):
    """
    Celery background worker task to anchor a newly issued credential on the blockchain.
    """
    try:
        credential = Credential.objects.select_related(
            'competency', 'competency__career_track', 'user'
        ).get(id=credential_id)

        proof = BlockchainService.record_credential_on_chain(credential)
        return f"Credential {credential_id} successfully anchored on Blockchain [{proof.network}]. Tx: {proof.transaction_hash}"
    except Credential.DoesNotExist:
        return f"Credential {credential_id} not found"
    except Exception as e:
        return f"Failed to anchor credential {credential_id}: {str(e)}"
