from typing import cast

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.common.schema import THROTTLED_RESPONSE
from apps.common.throttling import AiServiceBudget
from .adapters.http_adapter import AIProviderProtocolError, AIProviderUnavailable

from .serializers import (
    SkillGapAnalysisRequestSerializer,
    SkillGapAnalysisResponseSerializer,
    LearningRecommendationsResponseSerializer,
)
from .services import AIService
from apps.careers.models import CareerTrack


def provider_error_response(exc):
    if isinstance(exc, AIProviderUnavailable):
        payload = {'detail': 'AI provider is temporarily unavailable. Retry with the same request ID.',
                   'code': 'ai_provider_unavailable'}
        if exc.retry_after_seconds is not None:
            payload['retry_after_seconds'] = exc.retry_after_seconds
        return Response(payload, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    if isinstance(exc, AIProviderProtocolError):
        return Response({'detail': 'AI provider returned an invalid response.',
                         'code': 'ai_provider_invalid_response'},
                        status=status.HTTP_502_BAD_GATEWAY)
    return None


@extend_schema(tags=["AI Services"])
class SkillGapAnalysisView(APIView):
    """
    AI-powered skill gap analysis comparing student's acquired skills against target Career Track.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [AiServiceBudget]

    @extend_schema(
        summary="AI Skill Gap Analysis",
        description="Analyzes student's current skill profile against a target Career Track, computing match percentage and prioritized learning steps.",
        request=SkillGapAnalysisRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=SkillGapAnalysisResponseSerializer,
                description="Skill gap analysis report."
            ),
            **THROTTLED_RESPONSE,
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = SkillGapAnalysisRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, int], serializer.validated_data)
        career_track_id = validated_data['career_track_id']
        career_track = get_object_or_404(CareerTrack, pk=career_track_id)

        try:
            analysis = AIService.perform_skill_gap_analysis(
                user=request.user,
                career_track=career_track
            )
        except (AIProviderUnavailable, AIProviderProtocolError) as exc:
            return provider_error_response(exc)

        response_serializer = SkillGapAnalysisResponseSerializer(analysis)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["AI Services"])
class LearningRecommendationsView(APIView):
    """
    Personalized AI learning recommendations based on student's current progress and weak areas.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [AiServiceBudget]

    @extend_schema(
        summary="AI Learning Recommendations",
        description="Generates actionable learning recommendations based on student's mastery gaps and milestones.",
        responses={
            200: OpenApiResponse(
                response=LearningRecommendationsResponseSerializer,
                description="Personalized AI recommendations."
            ),
            **THROTTLED_RESPONSE,
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            recommendations = AIService.get_learning_recommendations(request.user)
        except (AIProviderUnavailable, AIProviderProtocolError) as exc:
            return provider_error_response(exc)
        response_serializer = LearningRecommendationsResponseSerializer(recommendations)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
