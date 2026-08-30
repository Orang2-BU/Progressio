from rest_framework import generics
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.credentials.models import Credential
from .serializers import PublicCredentialVerificationSerializer


@extend_schema(tags=["Verification"])
class PublicCredentialVerificationView(generics.RetrieveAPIView):
    """
    Public verification endpoint to verify credential authenticity and proof.
    Recruiters and external systems can verify without authentication.
    """
    queryset = Credential.objects.select_related(
        'competency', 'competency__career_track', 'user'
    ).prefetch_related('evidences').all()
    serializer_class = PublicCredentialVerificationSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'

    @extend_schema(
        summary="Verify Credential",
        description="Public endpoint to verify a credential's authenticity, status, score, student details, and portfolio evidence.",
        responses={
            200: OpenApiResponse(
                response=PublicCredentialVerificationSerializer,
                description="Credential proof verified successfully."
            )
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
