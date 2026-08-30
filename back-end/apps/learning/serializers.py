from rest_framework import serializers
from .models import Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model."""
    skill_title = serializers.CharField(
        source='skill.title', read_only=True
    )

    class Meta:
        model = Lesson
        fields = [
            'id', 'skill', 'skill_title', 'title',
            'content_type', 'content_url', 'duration', 'order',
            'created_at', 'updated_at'
        ]
