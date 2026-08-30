from django.contrib import admin
from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'skill', 'content_type', 'duration', 'order', 'created_at']
    list_filter = ['content_type', 'skill']
    search_fields = ['title']
