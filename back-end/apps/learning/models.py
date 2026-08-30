from django.db import models
from django.conf import settings
from apps.common.models import TimestampMixin
from apps.skills.models import Skill
from apps.competencies.models import Competency


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


class LessonCompletion(models.Model):
    """
    Records which lessons have been completed by which user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_completions'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='completions'
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lesson_completions'
        unique_together = ('user', 'lesson')
        verbose_name = 'Lesson Completion'
        verbose_name_plural = 'Lesson Completions'

    def __str__(self):
        return f"{self.user} completed {self.lesson.title}"


class SkillProgress(TimestampMixin):
    """
    Stores user mastery, XP, and confidence for a specific Skill.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='skill_progresses'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='user_progresses'
    )
    mastery = models.FloatField(
        default=0.0,
        help_text="Mastery percentage (0.0 to 100.0)."
    )
    xp = models.PositiveIntegerField(
        default=0,
        help_text="Total XP earned in this skill."
    )
    confidence = models.FloatField(
        default=0.0,
        help_text="Confidence metric (0.0 to 1.0)."
    )
    last_assessed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of last assessment evaluation."
    )

    class Meta:
        db_table = 'skill_progress'
        unique_together = ('user', 'skill')
        ordering = ['-updated_at']
        verbose_name = 'Skill Progress'
        verbose_name_plural = 'Skill Progresses'

    def __str__(self):
        return f"{self.user} - {self.skill.title}: {self.mastery}% ({self.xp} XP)"


class CompetencyProgress(models.Model):
    """
    Stores aggregated competency score and confidence for a User.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='competency_progresses'
    )
    competency = models.ForeignKey(
        Competency,
        on_delete=models.CASCADE,
        related_name='user_progresses'
    )
    score = models.FloatField(
        default=0.0,
        help_text="Aggregated competency score (0.0 to 100.0)."
    )
    confidence = models.FloatField(
        default=0.0,
        help_text="Overall confidence score (0.0 to 1.0)."
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'competency_progress'
        unique_together = ('user', 'competency')
        verbose_name = 'Competency Progress'
        verbose_name_plural = 'Competency Progresses'

    def __str__(self):
        return f"{self.user} - {self.competency.title}: Score {self.score}"
