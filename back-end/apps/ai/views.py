from typing import cast

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.common.schema import THROTTLED_RESPONSE
from apps.common.throttling import AiServiceBudget

from .serializers import (
    SkillGapAnalysisRequestSerializer,
    SkillGapAnalysisResponseSerializer,
    LearningRecommendationsResponseSerializer,
)
from .services import AIService
from apps.careers.models import CareerTrack


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

        analysis = AIService.perform_skill_gap_analysis(
            user=request.user,
            career_track=career_track
        )

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
        recommendations = AIService.get_learning_recommendations(request.user)
        response_serializer = LearningRecommendationsResponseSerializer(recommendations)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
