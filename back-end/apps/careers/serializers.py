from rest_framework import serializers
from .models import CareerTrack


class CareerTrackListSerializer(serializers.ModelSerializer):
    """Serializer for listing career tracks."""

    class Meta:
        model = CareerTrack
        fields = ['id', 'title', 'slug', 'description', 'is_active', 'created_at', 'updated_at']


class CareerTrackDetailSerializer(serializers.ModelSerializer):
    """Serializer for career track detail (includes competency count)."""
    competency_count = serializers.IntegerField(
        source='competencies.count',
        read_only=True,
        help_text="Number of competencies in this career track."
    )

    class Meta:
        model = CareerTrack
        fields = [
            'id', 'title', 'slug', 'description', 'is_active',
            'competency_count', 'created_at', 'updated_at'
        ]
