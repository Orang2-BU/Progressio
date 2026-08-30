from rest_framework import generics
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from .models import CareerTrack
from .serializers import CareerTrackListSerializer, CareerTrackDetailSerializer


@extend_schema(tags=["Career Tracks"])
class CareerTrackListView(generics.ListAPIView):
    """List all active career tracks."""
    queryset = CareerTrack.objects.filter(is_active=True)
    serializer_class = CareerTrackListSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="List Career Tracks")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["Career Tracks"])
class CareerTrackDetailView(generics.RetrieveAPIView):
    """Retrieve a single career track by ID."""
    queryset = CareerTrack.objects.filter(is_active=True)
    serializer_class = CareerTrackDetailSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="Career Track Detail")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
