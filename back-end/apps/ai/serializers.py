from rest_framework import serializers


class SkillGapAnalysisRequestSerializer(serializers.Serializer):
    career_track_id = serializers.IntegerField(
        required=True,
        help_text="ID of the target Career Track to evaluate skill gap against."
    )


class MissingSkillDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    difficulty = serializers.CharField()
    current_mastery = serializers.FloatField()
    estimated_minutes = serializers.IntegerField()


class AcquiredSkillDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    difficulty = serializers.CharField()


class SkillGapAnalysisResponseSerializer(serializers.Serializer):
    target_career_track = serializers.CharField()
    match_percentage = serializers.FloatField()
    summary = serializers.CharField()
    missing_skills = MissingSkillDetailSerializer(many=True)
    acquired_skills = AcquiredSkillDetailSerializer(many=True)
    recommended_priority_skill = serializers.CharField(allow_null=True)
    ai_insights = serializers.ListField(child=serializers.CharField())


class RecommendationItemSerializer(serializers.Serializer):
    type = serializers.CharField()
    title = serializers.CharField()
    reason = serializers.CharField()
    action_url = serializers.CharField()


class LearningRecommendationsResponseSerializer(serializers.Serializer):
    student_name = serializers.CharField()
    focus_area = serializers.CharField()
    recommendations = RecommendationItemSerializer(many=True)
    estimated_weekly_study_hours = serializers.FloatField()
