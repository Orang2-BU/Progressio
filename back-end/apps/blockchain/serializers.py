from rest_framework import serializers
from .models import BlockchainCredential, DemoAnchor


class BlockchainProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockchainCredential
        fields = [
            'credential_hash',
            'transaction_hash',
            'network',
            'block_number',
            'verified',
            'revoked',
            'created_at'
        ]


class DemoAnchorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemoAnchor
        fields = ['credential_id', 'credential_hash', 'network', 'chain_id',
                  'signer_address', 'transaction_hash', 'block_number', 'state',
                  'error_code', 'created_at', 'updated_at']
        read_only_fields = fields
