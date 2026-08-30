from rest_framework import serializers
from .models import Lesson, LessonCompletion, SkillProgress, CompetencyProgress


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


class LessonCompletionResponseSerializer(serializers.Serializer):
    status = serializers.CharField(default="completed")
    lesson_id = serializers.IntegerField()
    lesson_title = serializers.CharField()
    xp_earned = serializers.IntegerField()
    newly_completed = serializers.BooleanField()
    current_skill_mastery = serializers.FloatField()
    current_skill_xp = serializers.IntegerField()


class SkillProgressSerializer(serializers.ModelSerializer):
    skill_title = serializers.CharField(
        source='skill.title', read_only=True
    )
    competency_id = serializers.IntegerField(
        source='skill.competency_id', read_only=True
    )
    competency_title = serializers.CharField(
        source='skill.competency.title', read_only=True
    )

    class Meta:
        model = SkillProgress
        fields = [
            'id', 'skill', 'skill_title', 'competency_id', 'competency_title',
            'mastery', 'xp', 'confidence', 'last_assessed_at',
            'created_at', 'updated_at'
        ]


class CompetencyProgressSerializer(serializers.ModelSerializer):
    competency_title = serializers.CharField(
        source='competency.title', read_only=True
    )
    career_track_title = serializers.CharField(
        source='competency.career_track.title', read_only=True
    )

    class Meta:
        model = CompetencyProgress
        fields = [
            'id', 'competency', 'competency_title', 'career_track_title',
            'score', 'confidence', 'last_updated'
        ]


class UserProgressOverviewSerializer(serializers.Serializer):
    total_xp = serializers.IntegerField()
    completed_lessons_count = serializers.IntegerField()
    competencies = CompetencyProgressSerializer(
        source='competency_progresses', many=True
    )
    skills = SkillProgressSerializer(
        source='skill_progresses', many=True
    )


class MissingPrerequisiteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    current_mastery = serializers.FloatField()


class LearningPathNodeSerializer(serializers.Serializer):
    skill_id = serializers.IntegerField()
    skill_title = serializers.CharField()
    skill_slug = serializers.CharField()
    competency_id = serializers.IntegerField()
    competency_title = serializers.CharField()
    difficulty = serializers.CharField()
    status = serializers.ChoiceField(
        choices=['mastered', 'in_progress', 'available', 'locked']
    )
    mastery = serializers.FloatField()
    xp = serializers.IntegerField()
    missing_prerequisites = MissingPrerequisiteSerializer(many=True)
