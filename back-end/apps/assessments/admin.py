from django.contrib import admin
from .models import Assessment, Submission


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
