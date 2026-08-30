from rest_framework import serializers
from .models import Competency


class CompetencyListSerializer(serializers.ModelSerializer):
    career_track_title = serializers.CharField(
        source='career_track.title', read_only=True
    )

    class Meta:
        model = Competency
        fields = [
            'id', 'career_track', 'career_track_title',
            'title', 'slug', 'description', 'order',
            'created_at', 'updated_at'
        ]


class CompetencyDetailSerializer(serializers.ModelSerializer):
    career_track_title = serializers.CharField(
        source='career_track.title', read_only=True
    )
    skill_count = serializers.IntegerField(
        source='skills.count', read_only=True,
        help_text="Number of skills in this competency."
    )

    class Meta:
        model = Competency
        fields = [
            'id', 'career_track', 'career_track_title',
            'title', 'slug', 'description', 'order',
            'skill_count', 'created_at', 'updated_at'
        ]
