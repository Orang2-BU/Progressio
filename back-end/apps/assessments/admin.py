from django.contrib import admin
from .models import Assessment, Submission, DiagnosticAttempt, DiagnosticQuestion


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'skill', 'assessment_type', 'passing_score', 'max_score', 'created_at']
    list_filter = ['assessment_type', 'skill']
    search_fields = ['title', 'instructions']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['assessment', 'user', 'status', 'score', 'submitted_at', 'created_at']
    list_filter = ['status', 'assessment']
    search_fields = ['user__username', 'assessment__title', 'feedback']


@admin.register(DiagnosticQuestion)
class DiagnosticQuestionAdmin(admin.ModelAdmin):
    list_display = ['prompt', 'career_track', 'skill', 'order', 'is_active']
    list_filter = ['career_track', 'skill', 'is_active']
    search_fields = ['prompt', 'skill__title']


@admin.register(DiagnosticAttempt)
class DiagnosticAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'career_track', 'overall_score', 'completed_at']
    list_filter = ['career_track']
    search_fields = ['user__username']
