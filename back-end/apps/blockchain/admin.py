from django.contrib import admin
from .models import BlockchainCredential


@admin.register(BlockchainCredential)
class BlockchainCredentialAdmin(admin.ModelAdmin):
    list_display = ['credential', 'network', 'transaction_hash', 'verified', 'revoked', 'created_at']
    list_filter = ['network', 'verified', 'revoked']
    search_fields = ['credential__id', 'credential_hash', 'transaction_hash']
