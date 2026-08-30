from rest_framework import serializers
from .models import Assessment, Submission


class AssessmentListSerializer(serializers.ModelSerializer):
    skill_title = serializers.CharField(
        source='skill.title', read_only=True
    )

    class Meta:
        model = Assessment
        fields = [
            'id', 'skill', 'skill_title', 'title',
            'assessment_type', 'passing_score', 'max_score',
            'created_at', 'updated_at'
        ]


class AssessmentDetailSerializer(serializers.ModelSerializer):
    skill_title = serializers.CharField(
        source='skill.title', read_only=True
    )

    class Meta:
        model = Assessment
        fields = [
            'id', 'skill', 'skill_title', 'title',
            'assessment_type', 'instructions',
            'passing_score', 'max_score',
            'created_at', 'updated_at'
        ]


class SubmissionRequestSerializer(serializers.Serializer):
    content = serializers.DictField(
        required=False,
        default=dict,
        help_text="JSON payload containing quiz answers, code, or submission metadata."
    )
    score = serializers.FloatField(
        required=False,
        help_text="Optional custom score override."
    )


class SubmissionResponseSerializer(serializers.ModelSerializer):
    assessment_title = serializers.CharField(
        source='assessment.title', read_only=True
    )
    user_username = serializers.CharField(
        source='user.username', read_only=True
    )
    is_passed = serializers.BooleanField(
        read_only=True,
        help_text="True if score >= passing_score."
    )

    class Meta:
        model = Submission
        fields = [
            'id', 'assessment', 'assessment_title',
            'user', 'user_username', 'status',
            'content', 'score', 'feedback',
            'submitted_at', 'is_passed',
            'created_at', 'updated_at'
        ]
