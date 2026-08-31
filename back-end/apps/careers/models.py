from django.db import models
from apps.common.models import TimestampMixin


class CareerTrack(TimestampMixin):
    """
    Represents a career pathway.
    Example: Backend Engineering, Data Science, Mobile Development
    """
    class Difficulty(models.TextChoices):
        BEGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED = 'advanced', 'Advanced'

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)

    # --- Curriculum package fields (populated by import_curriculum) ---
    target_learner = models.TextField(
        blank=True,
        default='',
        help_text="Who this track is designed for, from the curriculum manifest."
    )
    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BEGINNER,
    )
    estimated_hours = models.PositiveIntegerField(
        default=0,
        help_text="Total estimated hours declared by the curriculum manifest."
    )
    curriculum_version = models.CharField(
        max_length=32,
        blank=True,
        default='',
        help_text="Version of the curriculum package that defines this track."
    )
    curriculum_schema_version = models.PositiveIntegerField(
        default=0,
        help_text="Schema version of the curriculum package."
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Curriculum manifest metadata (status, source, tags)."
    )
    is_managed = models.BooleanField(
        default=False,
        help_text="True when this record is owned by a curriculum package and must not be edited by hand."
    )

    class Meta:
        db_table = 'career_tracks'
        ordering = ['title']
        verbose_name = 'Career Track'
        verbose_name_plural = 'Career Tracks'

    def __str__(self):
        return self.title
