from rest_framework import generics
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import Skill
from .serializers import SkillListSerializer, SkillDetailSerializer
from apps.learning.serializers import LessonSerializer


@extend_schema(tags=["Skills"])
class SkillListView(generics.ListAPIView):
    """List all skills. Filterable by competency."""
    queryset = Skill.objects.select_related('competency').all()
    serializer_class = SkillListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['competency']

    @extend_schema(summary="List Skills")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["Skills"])
class SkillDetailView(generics.RetrieveAPIView):
    """Retrieve a single skill by ID with prerequisites."""
    queryset = Skill.objects.select_related('competency').prefetch_related(
        'prerequisites__required_skill'
    ).all()
    serializer_class = SkillDetailSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="Skill Detail")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["Skills"])
class SkillLessonsView(generics.ListAPIView):
    """List all lessons for a specific skill."""
    serializer_class = LessonSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        from apps.learning.models import Lesson
        if getattr(self, "swagger_fake_view", False):
            return Lesson.objects.none()
        return Lesson.objects.filter(skill_id=self.kwargs.get('pk')).order_by('order')

    @extend_schema(summary="Lessons for Skill")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
