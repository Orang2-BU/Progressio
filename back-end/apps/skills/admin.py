from django.contrib import admin
from .models import Skill, SkillPrerequisite


class SkillPrerequisiteInline(admin.TabularInline):
    model = SkillPrerequisite
    fk_name = 'skill'
    extra = 1


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['title', 'competency', 'difficulty', 'estimated_learning_minutes', 'created_at']
    list_filter = ['competency', 'difficulty']
    search_fields = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SkillPrerequisiteInline]


@admin.register(SkillPrerequisite)
class SkillPrerequisiteAdmin(admin.ModelAdmin):
    list_display = ['skill', 'required_skill']
    list_filter = ['skill', 'required_skill']
