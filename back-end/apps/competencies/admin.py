from django.contrib import admin
from .models import Competency


@admin.register(Competency)
class CompetencyAdmin(admin.ModelAdmin):
    list_display = ['title', 'career_track', 'order', 'created_at']
    list_filter = ['career_track']
    search_fields = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
