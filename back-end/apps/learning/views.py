from rest_framework import generics
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import Lesson
from .serializers import LessonSerializer


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
