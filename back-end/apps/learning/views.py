from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Lesson, SkillProgress
from .serializers import (
    LessonSerializer,
    LessonCompletionResponseSerializer,
    UserProgressOverviewSerializer,
    LearningPathNodeSerializer,
)
from .services import ProgressService, LearningPathService


@extend_schema(tags=["Learning"])
class LessonListView(generics.ListAPIView):
    """List all lessons. Filterable by skill."""
    queryset = Lesson.objects.select_related('skill').all()
    serializer_class = LessonSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['skill']

    @extend_schema(summary="List Lessons")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["Learning"])
class LessonDetailView(generics.RetrieveAPIView):
    """Retrieve a single lesson by ID."""
    queryset = Lesson.objects.select_related('skill').all()
    serializer_class = LessonSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="Lesson Detail")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["Learning"])
class LessonCompleteView(APIView):
    """
    Mark a lesson as completed by the authenticated user.
    Awards +50 XP and updates skill mastery.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Complete Lesson",
        description="Records completion of a learning material for the authenticated user and awards XP.",
        request=None,
        responses={
            200: OpenApiResponse(
                response=LessonCompletionResponseSerializer,
                description="Lesson marked as completed successfully."
            )
        }
    )
    def post(self, request, pk, *args, **kwargs):
        lesson = get_object_or_404(Lesson, pk=pk)
        completion, created, xp_earned = ProgressService.complete_lesson(
            user=request.user,
            lesson=lesson
        )

        skill_progress = SkillProgress.objects.filter(
            user=request.user,
            skill=lesson.skill
        ).first()

        data = {
            'status': 'completed',
            'lesson_id': lesson.id,
            'lesson_title': lesson.title,
            'xp_earned': xp_earned,
            'newly_completed': created,
            'current_skill_mastery': skill_progress.mastery if skill_progress else 0.0,
            'current_skill_xp': skill_progress.xp if skill_progress else 0,
        }
        return Response(data, status=status.HTTP_200_OK)


@extend_schema(tags=["Learning"])
class UserProgressView(APIView):
    """
    Get the overall progress and XP metrics for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="User Progress Overview",
        description="Returns total XP, completed lessons count, and detailed progress per competency and skill.",
        responses={
            200: OpenApiResponse(
                response=UserProgressOverviewSerializer,
                description="User learning progress overview."
            )
        }
    )
    def get(self, request, *args, **kwargs):
        overview_data = ProgressService.get_user_progress_overview(request.user)
        serializer = UserProgressOverviewSerializer(overview_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["Learning"])
class LearningPathView(APIView):
    """
    Get the recommended learning path and skill prerequisites graph status for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Learning Path Graph",
        description="Computes personalized skill nodes with status (mastered, in_progress, available, locked) and missing prerequisites.",
        responses={
            200: OpenApiResponse(
                response=LearningPathNodeSerializer(many=True),
                description="Personalized learning path nodes."
            )
        }
    )
    def get(self, request, *args, **kwargs):
        path_nodes = LearningPathService.get_learning_path(request.user)
        serializer = LearningPathNodeSerializer(path_nodes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
