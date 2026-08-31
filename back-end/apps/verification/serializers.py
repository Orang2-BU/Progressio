from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from apps.credentials.models import Credential
from apps.credentials.serializers import EvidenceSerializer, build_verification_url
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
    is_valid = serializers.SerializerMethodField()
    integrity_verified = serializers.SerializerMethodField()
    integrity_reason = serializers.SerializerMethodField()
    verification_url = serializers.SerializerMethodField()
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
            'integrity_verified',
            'integrity_reason',
            'verification_url',
            'created_at'
        ]

    @extend_schema_field(serializers.CharField())
    def get_student_name(self, obj) -> str:
        # Read from metadata snapshot first, fallback to user full name/username
        if isinstance(obj.metadata, dict) and obj.metadata.get('student_name'):
            return obj.metadata['student_name']
        return obj.user.get_full_name() or obj.user.username

    def _integrity(self, obj):
        if not hasattr(obj, '_integrity_cache'):
            from apps.blockchain.services import BlockchainService
            obj._integrity_cache = BlockchainService.verify_credential_integrity(obj)
        return obj._integrity_cache

    @extend_schema_field(serializers.BooleanField())
    def get_integrity_verified(self, obj) -> bool:
        return self._integrity(obj)[0]

    @extend_schema_field(serializers.BooleanField())
    def get_is_valid(self, obj) -> bool:
        return obj.status == Credential.Status.ISSUED and self._integrity(obj)[0]

    @extend_schema_field(serializers.CharField())
    def get_integrity_reason(self, obj) -> str:
        is_intact, _, proof = self._integrity(obj)
        if proof is None:
            return 'proof_missing'
        if proof.revoked or obj.status == Credential.Status.REVOKED:
            return 'revoked'
        return 'verified' if is_intact else 'hash_mismatch_or_unconfirmed'

    @extend_schema_field(serializers.URLField())
    def get_verification_url(self, obj) -> str:
        return build_verification_url(self, obj)
