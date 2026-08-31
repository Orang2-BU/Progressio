from django.contrib import admin
from .models import Lesson, LessonCompletion, SkillProgress, CompetencyProgress


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'skill', 'content_type', 'duration', 'order', 'created_at']
    list_filter = ['content_type', 'skill']
    search_fields = ['title']


@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed_at']
    list_filter = ['user', 'lesson__skill']
    search_fields = ['user__username', 'lesson__title']


@admin.register(SkillProgress)
class SkillProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill', 'mastery', 'xp', 'confidence', 'last_assessed_at', 'updated_at']
    list_filter = ['skill__competency', 'user']
    search_fields = ['user__username', 'skill__title']


@admin.register(CompetencyProgress)
class CompetencyProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'competency', 'score', 'confidence', 'last_updated']
    list_filter = ['competency__career_track', 'user']
    search_fields = ['user__username', 'competency__title']
