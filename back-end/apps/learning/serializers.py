from rest_framework import serializers
from .models import Lesson, LessonCompletion, SkillProgress, CompetencyProgress, StudyStep


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
            'provider', 'authority_level', 'license', 'license_url',
            'attribution_required', 'link_status',
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


class RoadmapTargetSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['skill', 'competency', 'career_track'])
    slug = serializers.CharField()
    title = serializers.CharField()


class RoadmapStepSerializer(serializers.Serializer):
    order = serializers.IntegerField()
    skill_id = serializers.IntegerField()
    skill_slug = serializers.CharField()
    skill_title = serializers.CharField()
    competency_title = serializers.CharField()
    difficulty = serializers.CharField()
    estimated_minutes = serializers.IntegerField()
    mastery = serializers.FloatField()
    prerequisites = serializers.ListField(child=serializers.CharField())
    is_target = serializers.BooleanField()


class RoadmapSatisfiedSerializer(serializers.Serializer):
    skill_slug = serializers.CharField()
    skill_title = serializers.CharField()
    mastery = serializers.FloatField()


class RoadmapSerializer(serializers.Serializer):
    target = RoadmapTargetSerializer()
    total_steps = serializers.IntegerField()
    remaining_minutes = serializers.IntegerField()
    remaining_hours = serializers.FloatField()
    already_satisfied = RoadmapSatisfiedSerializer(many=True)
    steps = RoadmapStepSerializer(many=True)


class StudyStepSerializer(serializers.ModelSerializer):
    """
    Public view of a study step. ``checkpoint_answer`` is deliberately absent:
    checkpoints are graded server-side, like every other answer in Progressio.
    """
    study_url = serializers.CharField(read_only=True)
    provider = serializers.CharField(source='lesson.provider', read_only=True)
    license = serializers.CharField(source='lesson.license', read_only=True)

    class Meta:
        model = StudyStep
        fields = [
            'id', 'lesson', 'order', 'prompt', 'checkpoint_question',
            'estimated_minutes', 'study_url', 'provider', 'license',
        ]


class StudyCheckpointRequestSerializer(serializers.Serializer):
    answer = serializers.CharField(max_length=255)


class StudyCheckpointResponseSerializer(serializers.Serializer):
    correct = serializers.BooleanField()
    feedback = serializers.CharField()
