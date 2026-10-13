"""Low-cost Base Sepolia demo anchoring using a self-transfer carrying only a digest."""
import json
import os
from urllib.request import Request, urlopen

from django.db import transaction
from eth_account import Account
from eth_utils import to_checksum_address

from apps.credentials.models import Credential
from .models import DemoAnchor
from .services import BlockchainService


CHAIN_ID = 84532
NETWORK = 'base-sepolia'
CONFIRMATIONS = 2


class DemoAnchorError(RuntimeError):
    pass


class BaseSepoliaRPC:
    def __init__(self, url=None, timeout=8):
        self.url = url or os.getenv('DEMO_BLOCKCHAIN_RPC_URL', 'https://sepolia.base.org')
        self.timeout = timeout

    def call(self, method, params):
        request = Request(self.url, data=json.dumps({'jsonrpc': '2.0', 'id': 1,
            'method': method, 'params': params}).encode(),
            headers={'Content-Type': 'application/json'}, method='POST')
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode())
        except Exception as exc:
            raise DemoAnchorError('rpc_unavailable') from exc
        if not isinstance(payload, dict) or payload.get('error') or 'result' not in payload:
            raise DemoAnchorError('rpc_error')
        return payload['result']


def queue_demo_anchor(credential, rpc=None):
    if credential.status != Credential.Status.DRAFT or credential.metadata.get('mode') != 'demo':
        raise DemoAnchorError('demo_credential_required')
    signer = os.getenv('DEMO_ANCHOR_SIGNER_ADDRESS', '').strip()
    if not signer:
        raise DemoAnchorError('signer_not_configured')
    try:
        signer = to_checksum_address(signer)
    except ValueError as exc:
        raise DemoAnchorError('signer_not_configured') from exc
    digest = BlockchainService.compute_credential_hash(credential)
    anchor, _ = DemoAnchor.objects.get_or_create(credential=credential, defaults={
        'credential_hash': digest, 'network': NETWORK, 'chain_id': CHAIN_ID,
        'signer_address': signer,
    })
    if anchor.credential_hash != digest or anchor.chain_id != CHAIN_ID or anchor.signer_address.lower() != signer.lower():
        raise DemoAnchorError('anchor_identity_conflict')
    return anchor


def process_demo_anchor(anchor_id, rpc=None):
    """Prepare a replay-safe signed transaction, broadcast it, then verify receipt and calldata."""
    rpc = rpc or BaseSepoliaRPC()
    private_key = os.getenv('DEMO_ANCHOR_PRIVATE_KEY', '').strip()
    if not private_key:
        raise DemoAnchorError('signer_not_configured')
    account = Account.from_key(private_key)
    with transaction.atomic():
        anchor = DemoAnchor.objects.select_for_update().get(pk=anchor_id)
        credential = Credential.objects.select_related('competency', 'competency__career_track', 'user').get(pk=anchor.credential_id)
        if credential.status != Credential.Status.DRAFT or credential.metadata.get('mode') != 'demo':
            anchor.state, anchor.error_code = DemoAnchor.State.FAILED, 'credential_not_demo'
            anchor.save(update_fields=['state', 'error_code', 'updated_at'])
            return anchor
        if BlockchainService.compute_credential_hash(credential) != anchor.credential_hash:
            anchor.state, anchor.error_code = DemoAnchor.State.FAILED, 'hash_mismatch'
            anchor.save(update_fields=['state', 'error_code', 'updated_at'])
            return anchor
        if anchor.state == DemoAnchor.State.CONFIRMED:
            return anchor
        if anchor.signer_address.lower() != account.address.lower():
            raise DemoAnchorError('signer_mismatch')
        if not anchor.raw_signed_transaction:
            if int(rpc.call('eth_chainId', []), 16) != CHAIN_ID:
                raise DemoAnchorError('wrong_chain')
            nonce = int(rpc.call('eth_getTransactionCount', [account.address, 'pending']), 16)
            price = int(rpc.call('eth_gasPrice', []), 16)
            max_gwei = int(os.getenv('DEMO_ANCHOR_MAX_FEE_GWEI', '10'))
            if price > max_gwei * 10**9:
                raise DemoAnchorError('fee_cap_exceeded')
            tx = {'chainId': CHAIN_ID, 'nonce': nonce, 'to': account.address, 'value': 0,
                'data': '0x' + anchor.credential_hash, 'gas': 50000, 'gasPrice': price}
            signed = Account.sign_transaction(tx, private_key)
            raw = signed.raw_transaction.hex()
            anchor.raw_signed_transaction = raw if raw.startswith('0x') else '0x' + raw
            anchor.transaction_hash = signed.hash.hex()
            if not anchor.transaction_hash.startswith('0x'):
                anchor.transaction_hash = '0x' + anchor.transaction_hash
            anchor.signer_address = to_checksum_address(account.address)
            anchor.save(update_fields=['raw_signed_transaction', 'transaction_hash', 'signer_address', 'updated_at'])
    # Re-broadcast is idempotent because it is always exactly the same signed transaction.
    try:
        submitted_hash = rpc.call('eth_sendRawTransaction', [anchor.raw_signed_transaction])
        if not isinstance(submitted_hash, str) or submitted_hash.lower() != anchor.transaction_hash.lower():
            raise DemoAnchorError('transaction_hash_mismatch')
    except DemoAnchorError:
        # Node commonly says "already known" after a previous accepted broadcast.
        tx = rpc.call('eth_getTransactionByHash', [anchor.transaction_hash])
        if not tx:
            raise
    receipt = rpc.call('eth_getTransactionReceipt', [anchor.transaction_hash])
    if not receipt:
        DemoAnchor.objects.filter(pk=anchor.pk).update(state=DemoAnchor.State.SUBMITTED, error_code='')
        anchor.refresh_from_db()
        return anchor
    if int(receipt.get('status', '0x0'), 16) != 1:
        DemoAnchor.objects.filter(pk=anchor.pk).update(state=DemoAnchor.State.FAILED, error_code='transaction_reverted')
        anchor.refresh_from_db()
        return anchor
    tx = rpc.call('eth_getTransactionByHash', [anchor.transaction_hash])
    if (not tx or tx.get('from', '').lower() != anchor.signer_address.lower()
            or tx.get('to', '').lower() != anchor.signer_address.lower()
            or tx.get('input', '').lower() != ('0x' + anchor.credential_hash).lower()):
        DemoAnchor.objects.filter(pk=anchor.pk).update(state=DemoAnchor.State.FAILED, error_code='transaction_mismatch')
        anchor.refresh_from_db()
        return anchor
    height = int(receipt['blockNumber'], 16)
    head = int(rpc.call('eth_blockNumber', []), 16)
    state = DemoAnchor.State.CONFIRMED if head - height + 1 >= CONFIRMATIONS else DemoAnchor.State.SUBMITTED
    DemoAnchor.objects.filter(pk=anchor.pk).update(state=state, block_number=height, error_code='')
    anchor.refresh_from_db()
    return anchor
