from django.db import models
from apps.common.models import TimestampMixin


class CareerTrack(TimestampMixin):
    """
    Represents a career pathway.
    Example: Backend Engineering, Data Science, Mobile Development
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'career_tracks'
        ordering = ['title']
        verbose_name = 'Career Track'
        verbose_name_plural = 'Career Tracks'

    def __str__(self):
        return self.title
