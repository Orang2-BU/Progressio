from rest_framework import serializers
from .models import Skill, SkillPrerequisite


class SkillPrerequisiteSerializer(serializers.ModelSerializer):
    required_skill_title = serializers.CharField(
        source='required_skill.title', read_only=True
    )

    class Meta:
        model = SkillPrerequisite
        fields = ['id', 'required_skill', 'required_skill_title']


class SkillListSerializer(serializers.ModelSerializer):
    competency_title = serializers.CharField(
        source='competency.title', read_only=True
    )

    class Meta:
        model = Skill
        fields = [
            'id', 'competency', 'competency_title',
            'title', 'slug', 'description', 'difficulty',
            'estimated_learning_minutes', 'created_at', 'updated_at'
        ]


class SkillDetailSerializer(serializers.ModelSerializer):
    competency_title = serializers.CharField(
        source='competency.title', read_only=True
    )
    prerequisites = SkillPrerequisiteSerializer(many=True, read_only=True)
    lesson_count = serializers.IntegerField(
        source='lessons.count', read_only=True,
        help_text="Number of lessons for this skill."
    )

    class Meta:
        model = Skill
        fields = [
            'id', 'competency', 'competency_title',
            'title', 'slug', 'description', 'difficulty',
            'estimated_learning_minutes', 'prerequisites',
            'lesson_count', 'created_at', 'updated_at'
        ]
