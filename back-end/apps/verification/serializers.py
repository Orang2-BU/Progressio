from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from apps.credentials.models import Credential
from apps.credentials.serializers import EvidenceSerializer
from apps.blockchain.serializers import BlockchainProofSerializer


class PublicCredentialVerificationSerializer(serializers.ModelSerializer):
    """
    Public-facing serializer for verifying credentials without requiring authentication.
    Used by recruiters, companies, and external platforms.
    """
    credential_id = serializers.UUIDField(source='id', read_only=True)
    student_name = serializers.SerializerMethodField()
    competency_title = serializers.CharField(
        source='competency.title', read_only=True
    )
    career_track_title = serializers.CharField(
        source='competency.career_track.title', read_only=True
    )
    is_valid = serializers.BooleanField(read_only=True)
    evidences = EvidenceSerializer(many=True, read_only=True)
    blockchain_proof = BlockchainProofSerializer(read_only=True)

    class Meta:
        model = Credential
        fields = [
            'credential_id',
            'is_valid',
            'status',
            'student_name',
            'competency_title',
            'career_track_title',
            'score',
            'issued_at',
            'evidences',
            'blockchain_proof',
            'created_at'
        ]

    @extend_schema_field(serializers.CharField())
    def get_student_name(self, obj) -> str:
        # Read from metadata snapshot first, fallback to user full name/username
        if isinstance(obj.metadata, dict) and obj.metadata.get('student_name'):
            return obj.metadata['student_name']
        return obj.user.get_full_name() or obj.user.username
