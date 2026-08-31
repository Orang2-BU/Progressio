from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Assessment, Submission
from .serializers import (
    AssessmentListSerializer,
    AssessmentDetailSerializer,
    SubmissionRequestSerializer,
    SubmissionResponseSerializer,
)
from .services import AssessmentEvaluationService


@extend_schema(tags=["Assessments"])
class AssessmentListView(generics.ListAPIView):
    """List all assessments. Filterable by skill."""
    queryset = Assessment.objects.select_related('skill').all()
    serializer_class = AssessmentListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['skill']

    @extend_schema(summary="List Assessments")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["Assessments"])
class AssessmentDetailView(generics.RetrieveAPIView):
    """Retrieve a single assessment by ID."""
    queryset = Assessment.objects.select_related('skill').all()
    serializer_class = AssessmentDetailSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="Assessment Detail")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["Assessments"])
class AssessmentSubmitView(APIView):
    """
    Submit and evaluate an assessment.
    Transitions through the state machine: submitted -> evaluating -> completed.
    Updates skill mastery and XP upon passing.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Submit Assessment",
        description="Submit answers/code for an assessment. Triggers automated evaluation and progress update if passed.",
        request=SubmissionRequestSerializer,
        responses={
            201: OpenApiResponse(
                response=SubmissionResponseSerializer,
                description="Assessment evaluated successfully."
            )
        }
    )
    def post(self, request, pk, *args, **kwargs):
        assessment = get_object_or_404(Assessment, pk=pk)
        serializer = SubmissionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        content = serializer.validated_data.get('content', {})
        submission = AssessmentEvaluationService.submit_and_evaluate(
            user=request.user,
            assessment=assessment,
            content=content,
        )

        response_serializer = SubmissionResponseSerializer(submission)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
