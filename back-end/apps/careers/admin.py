from django.contrib import admin
from .models import CareerTrack


@admin.register(CareerTrack)
class CareerTrackAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
