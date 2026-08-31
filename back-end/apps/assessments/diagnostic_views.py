from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.careers.models import CareerTrack

from .models import DiagnosticAttempt, DiagnosticQuestion
from .serializers import (
    DiagnosticAttemptSerializer,
    DiagnosticQuestionSerializer,
    DiagnosticSubmissionSerializer,
)
from .services import DiagnosticService


@extend_schema(tags=['Diagnostics'])
class DiagnosticQuestionListView(generics.ListAPIView):
    serializer_class = DiagnosticQuestionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return DiagnosticQuestion.objects.none()
        return DiagnosticQuestion.objects.filter(
            career_track_id=self.kwargs['career_track_id'],
            career_track__is_active=True,
            is_active=True,
        ).select_related('skill')


@extend_schema(tags=['Diagnostics'])
class DiagnosticSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=DiagnosticSubmissionSerializer,
        responses={201: DiagnosticAttemptSerializer},
        summary='Submit and grade a career diagnostic',
    )
    def post(self, request, career_track_id):
        serializer = DiagnosticSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        career_track = get_object_or_404(CareerTrack, pk=career_track_id, is_active=True)
        attempt = DiagnosticService.submit(
            user=request.user,
            career_track=career_track,
            answers=serializer.validated_data['answers'],
        )
        return Response(DiagnosticAttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Diagnostics'])
class LatestDiagnosticAttemptView(generics.RetrieveAPIView):
    serializer_class = DiagnosticAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        queryset = DiagnosticAttempt.objects.filter(user=self.request.user)
        career_track_id = self.request.query_params.get('career_track')
        if career_track_id:
            queryset = queryset.filter(career_track_id=career_track_id)
        return get_object_or_404(queryset)
