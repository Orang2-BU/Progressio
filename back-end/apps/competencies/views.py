from rest_framework import generics
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import Competency
from .serializers import CompetencyListSerializer, CompetencyDetailSerializer


@extend_schema(tags=["Competencies"])
class CompetencyListView(generics.ListAPIView):
    """List all competencies. Filterable by career_track."""
    queryset = Competency.objects.select_related('career_track').all()
    serializer_class = CompetencyListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['career_track']

    @extend_schema(summary="List Competencies")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["Competencies"])
class CompetencyDetailView(generics.RetrieveAPIView):
    """Retrieve a single competency by ID."""
    queryset = Competency.objects.select_related('career_track').all()
    serializer_class = CompetencyDetailSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="Competency Detail")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
