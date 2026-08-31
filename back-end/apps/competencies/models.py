from django.db import models
from apps.common.models import TimestampMixin
from apps.careers.models import CareerTrack


class Competency(TimestampMixin):
    """
    Represents a competency inside a career track.
    Examples: Programming Fundamentals, Database Engineering, API Development
    """
    career_track = models.ForeignKey(
        CareerTrack,
        on_delete=models.CASCADE,
        related_name='competencies'
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, default='')
    order = models.PositiveIntegerField(default=0, help_text="Display order within career track.")

    # --- Curriculum package fields (populated by import_curriculum) ---
    estimated_hours = models.PositiveIntegerField(
        default=0,
        help_text="Estimated hours to reach this competency."
    )
    learning_outcomes = models.JSONField(
        default=list,
        blank=True,
        help_text="What a learner can do once this competency is reached."
    )
    observable_behaviors = models.JSONField(
        default=list,
        blank=True,
        help_text="Externally observable evidence that this competency is held."
    )
    is_managed = models.BooleanField(
        default=False,
        help_text="True when this record is owned by a curriculum package."
    )

    class Meta:
        db_table = 'competencies'
        ordering = ['career_track', 'order']
        verbose_name = 'Competency'
        verbose_name_plural = 'Competencies'

    def __str__(self):
        return self.title


class CompetencyPrerequisite(models.Model):
    """
    Competency-level dependency graph, mirroring SkillPrerequisite one level up.
    Example: API Development requires Backend and Web Foundations.
    """
    competency = models.ForeignKey(
        Competency,
        on_delete=models.CASCADE,
        related_name='prerequisites'
    )
    required_competency = models.ForeignKey(
        Competency,
        on_delete=models.CASCADE,
        related_name='required_by'
    )

    class Meta:
        db_table = 'competency_prerequisites'
        unique_together = ('competency', 'required_competency')
        verbose_name = 'Competency Prerequisite'
        verbose_name_plural = 'Competency Prerequisites'

    def __str__(self):
        return f"{self.competency.title} requires {self.required_competency.title}"
