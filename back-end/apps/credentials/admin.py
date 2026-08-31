from django.contrib import admin
from .models import Credential, Evidence


class EvidenceInline(admin.TabularInline):
    model = Evidence
    extra = 1


@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'competency', 'status', 'score', 'issued_at', 'created_at']
    list_filter = ['status', 'competency']
    search_fields = ['id', 'user__username', 'competency__title']
    inlines = [EvidenceInline]


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ['credential', 'github_url', 'demo_url', 'created_at']
    search_fields = ['credential__id', 'github_url', 'demo_url']
