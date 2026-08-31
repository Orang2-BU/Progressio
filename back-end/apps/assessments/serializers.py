from rest_framework import serializers
import json
from .models import Assessment, Submission, DiagnosticQuestion, DiagnosticAttempt


class AssessmentListSerializer(serializers.ModelSerializer):
    skill_title = serializers.CharField(
        source='skill.title', read_only=True
    )

    class Meta:
        model = Assessment
        fields = [
            'id', 'skill', 'skill_title', 'title',
            'assessment_type', 'passing_score', 'max_score',
            'evaluation_mode',
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
            'evaluation_mode',
            'created_at', 'updated_at'
        ]


class SubmissionRequestSerializer(serializers.Serializer):
    content = serializers.DictField(
        required=False,
        default=dict,
        help_text="JSON payload containing quiz answers, code, or submission metadata."
    )

    def validate_content(self, value):
        if len(json.dumps(value, ensure_ascii=False).encode('utf-8')) > 200_000:
            raise serializers.ValidationError('Submission content must not exceed 200 KB.')
        return value

    def validate(self, attrs):
        if 'score' in self.initial_data:
            raise serializers.ValidationError({
                'score': 'Score is calculated by the server and cannot be supplied by clients.'
            })
        return attrs


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


class DiagnosticQuestionSerializer(serializers.ModelSerializer):
    skill_title = serializers.CharField(source='skill.title', read_only=True)

    class Meta:
        model = DiagnosticQuestion
        fields = ['id', 'skill', 'skill_title', 'prompt', 'options', 'order']


class DiagnosticSubmissionSerializer(serializers.Serializer):
    answers = serializers.DictField(
        child=serializers.CharField(allow_blank=True),
        allow_empty=False,
        help_text="Map of diagnostic question IDs to selected answer values.",
    )

class DiagnosticAttemptSerializer(serializers.ModelSerializer):
    career_track_title = serializers.CharField(source='career_track.title', read_only=True)
    recommended_skill_ids = serializers.ListField(
        source='weak_skill_ids',
        child=serializers.IntegerField(),
        read_only=True,
    )

    class Meta:
        model = DiagnosticAttempt
        fields = [
            'id', 'career_track', 'career_track_title', 'overall_score',
            'skill_scores', 'recommended_skill_ids', 'completed_at',
        ]
