from django.db import models
from apps.common.models import TimestampMixin
from apps.skills.models import Skill


class Lesson(TimestampMixin):
    """
    Represents learning materials for a skill.
    Content types: video, article, exercise, reading
    """

    class ContentType(models.TextChoices):
        VIDEO = 'video', 'Video'
        ARTICLE = 'article', 'Article'
        EXERCISE = 'exercise', 'Exercise'
        READING = 'reading', 'Reading'

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=255)
    content_type = models.CharField(
        max_length=20,
        choices=ContentType.choices,
        default=ContentType.ARTICLE,
    )
    content_url = models.URLField(max_length=500, blank=True, default='')
    duration = models.PositiveIntegerField(
        default=0,
        help_text="Duration in minutes."
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order of lesson within the skill."
    )

    class Meta:
        db_table = 'lessons'
        ordering = ['skill', 'order']
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'

    def __str__(self):
        return f"{self.skill.title} - {self.title}"
