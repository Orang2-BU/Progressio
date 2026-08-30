from rest_framework import serializers
from .models import Credential, Evidence


class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = [
            'id', 'submission', 'github_url', 'file_url',
            'demo_url', 'notes', 'created_at'
        ]


class CredentialListSerializer(serializers.ModelSerializer):
    competency_title = serializers.CharField(
        source='competency.title', read_only=True
    )
    career_track_title = serializers.CharField(
        source='competency.career_track.title', read_only=True
    )

    class Meta:
        model = Credential
        fields = [
            'id', 'competency', 'competency_title',
            'career_track_title', 'status', 'score',
            'issued_at', 'created_at'
        ]


class CredentialDetailSerializer(serializers.ModelSerializer):
    competency_title = serializers.CharField(
        source='competency.title', read_only=True
    )
    career_track_title = serializers.CharField(
        source='competency.career_track.title', read_only=True
    )
    user_username = serializers.CharField(
        source='user.username', read_only=True
    )
    evidences = EvidenceSerializer(many=True, read_only=True)
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Credential
        fields = [
            'id', 'user', 'user_username',
            'competency', 'competency_title',
            'career_track_title', 'status', 'score',
            'is_valid', 'issued_at', 'metadata',
            'evidences', 'created_at', 'updated_at'
        ]


class CredentialIssueRequestSerializer(serializers.Serializer):
    competency_id = serializers.IntegerField(
        required=True,
        help_text="ID of the completed competency to issue a credential for."
    )
    github_url = serializers.URLField(
        required=False,
        allow_blank=True,
        default='',
        help_text="Supporting GitHub repository URL."
    )
    demo_url = serializers.URLField(
        required=False,
        allow_blank=True,
        default='',
        help_text="Supporting live demonstration URL."
    )
    file_url = serializers.URLField(
        required=False,
        allow_blank=True,
        default='',
        help_text="Supporting artifact or document URL."
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        help_text="Portfolio or project notes."
    )
    submission_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        default=None,
        help_text="Optional associated assessment submission ID."
    )
