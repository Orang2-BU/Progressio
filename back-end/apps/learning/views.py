from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from apps.careers.models import CareerTrack
from apps.competencies.models import Competency
from apps.skills.models import Skill

from .models import Lesson, SkillProgress, StudyStep
from .serializers import (
    LessonSerializer,
    LessonCompletionResponseSerializer,
    UserProgressOverviewSerializer,
    LearningPathNodeSerializer,
    RoadmapSerializer,
    StudyStepSerializer,
    StudyCheckpointRequestSerializer,
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
        track_slug = request.query_params.get('career_track')
        career_track = get_object_or_404(CareerTrack, slug=track_slug) if track_slug else None
        path_nodes = LearningPathService.get_learning_path(request.user, career_track=career_track)
        serializer = LearningPathNodeSerializer(path_nodes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["Learning"])
class RoadmapView(APIView):
    """
    Route from where the learner is now to a target they chose.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Personalized Roadmap",
        description=(
            "Walks the prerequisite graph backwards from a chosen target and returns only "
            "the skills still to be learned, ordered so every prerequisite comes first. "
            "Skills already held at 70 mastery are reported as satisfied and drop out of "
            "the route. Provide exactly one of skill, competency, or career_track."
        ),
        parameters=[
            OpenApiParameter('skill', str, description='Target skill slug.'),
            OpenApiParameter('competency', str, description='Target competency slug.'),
            OpenApiParameter('career_track', str, description='Target career track slug.'),
        ],
        responses={
            200: OpenApiResponse(
                response=RoadmapSerializer,
                description="Ordered roadmap with remaining effort."
            )
        }
    )
    def get(self, request, *args, **kwargs):
        params = {
            'target_skill': (Skill, request.query_params.get('skill')),
            'target_competency': (Competency, request.query_params.get('competency')),
            'career_track': (CareerTrack, request.query_params.get('career_track')),
        }
        given = {key: value for key, (_, value) in params.items() if value}
        if len(given) != 1:
            return Response(
                {'detail': 'Provide exactly one of skill, competency, or career_track.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        key = next(iter(given))
        model, slug = params[key]
        target = get_object_or_404(model, slug=slug)

        try:
            roadmap = LearningPathService.get_roadmap(request.user, **{key: target})
        except ValueError as error:
            return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RoadmapSerializer(roadmap)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["Learning"])
class SkillStudyPlanView(generics.ListAPIView):
    """
    The authored study plan for one skill: which section of which source to
    read, and what to do there. The material stays at the publisher.
    """
    serializer_class = StudyStepSerializer
    permission_classes = [AllowAny]
    # Schema generation introspects the view without URL kwargs present.
    queryset = StudyStep.objects.none()

    @extend_schema(
        summary="Skill Study Plan",
        description=(
            "Ordered study steps for a skill. Each step deep-links into a licensed "
            "source and states what the learner should do with that section. "
            "Checkpoint answers are never included."
        ),
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        skill = get_object_or_404(Skill, slug=self.kwargs['slug'])
        return StudyStep.objects.filter(
            lesson__skill=skill
        ).select_related('lesson').order_by('lesson__order', 'order')


@extend_schema(tags=["Learning"])
class StudyCheckpointView(APIView):
    """
    Check one study step's checkpoint answer.

    Graded server-side against an answer the client never receives, for the same
    reason quiz answer keys stay server-side.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Submit Study Checkpoint",
        request=StudyCheckpointRequestSerializer,
        responses={
            200: OpenApiResponse(description="Whether the checkpoint answer was correct."),
        },
    )
    def post(self, request, pk, *args, **kwargs):
        step = get_object_or_404(StudyStep, pk=pk)
        serializer = StudyCheckpointRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        given = serializer.validated_data['answer'].strip().casefold()
        expected = step.checkpoint_answer.strip().casefold()
        correct = given == expected

        return Response(
            {
                'correct': correct,
                'feedback': (
                    'Correct.' if correct
                    else 'Not quite. Re-read the linked section and try again.'
                ),
            },
            status=status.HTTP_200_OK,
        )
