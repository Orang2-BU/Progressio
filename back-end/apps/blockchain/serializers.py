from rest_framework import serializers
from .models import BlockchainCredential


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
