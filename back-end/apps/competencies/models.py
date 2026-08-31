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

    class Meta:
        db_table = 'competencies'
        ordering = ['career_track', 'order']
        verbose_name = 'Competency'
        verbose_name_plural = 'Competencies'

    def __str__(self):
        return self.title
