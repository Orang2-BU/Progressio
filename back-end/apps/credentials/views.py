from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Credential
from .serializers import (
    CredentialListSerializer,
    CredentialDetailSerializer,
    CredentialIssueRequestSerializer,
)
from .services import CredentialService
from apps.competencies.models import Competency


@extend_schema(tags=["Credentials"])
class CredentialListView(generics.ListAPIView):
    """
    List all credentials belonging to the authenticated user.
    Filterable by status and competency.
    """
    serializer_class = CredentialListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'competency']

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Credential.objects.none()
        return Credential.objects.filter(
            user=self.request.user
        ).select_related('competency', 'competency__career_track')

    @extend_schema(summary="List User Credentials")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["Credentials"])
class CredentialDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific credential with evidence and snapshot metadata.
    """
    serializer_class = CredentialDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Credential.objects.none()
        return Credential.objects.filter(
            user=self.request.user
        ).select_related('competency', 'competency__career_track', 'user').prefetch_related('evidences')

    @extend_schema(summary="Credential Detail")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["Credentials"])
class CredentialIssueView(APIView):
    """
    Issue a new verified credential for a completed competency.
    Requires minimum competency achievement score >= 70%.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Issue Credential",
        description="Issues a verified credential for a competency if passing criteria (>=70%) are met.",
        request=CredentialIssueRequestSerializer,
        responses={
            201: OpenApiResponse(
                response=CredentialDetailSerializer,
                description="Credential issued successfully."
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = CredentialIssueRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        competency_id = serializer.validated_data['competency_id']
        competency = get_object_or_404(Competency, pk=competency_id)

        evidence_data = {
            'github_url': serializer.validated_data.get('github_url', ''),
            'demo_url': serializer.validated_data.get('demo_url', ''),
            'file_url': serializer.validated_data.get('file_url', ''),
            'notes': serializer.validated_data.get('notes', ''),
            'submission_id': serializer.validated_data.get('submission_id'),
        }

        credential = CredentialService.issue_credential(
            user=request.user,
            competency=competency,
            evidence_data=evidence_data
        )

        response_serializer = CredentialDetailSerializer(
            credential,
            context={'request': request},
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
