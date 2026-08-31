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

    # --- Curriculum package fields (populated by import_curriculum) ---
    source_id = models.SlugField(
        max_length=255,
        blank=True,
        default='',
        help_text="Curriculum resource ID this lesson points at. Empty for hand-authored lessons."
    )
    provider = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Publisher of the linked resource, e.g. MDN, IETF, OWASP."
    )
    authority_level = models.CharField(
        max_length=64,
        blank=True,
        default='',
        help_text="How authoritative the source is, e.g. industry-standard."
    )
    source_verified_at = models.DateField(
        null=True,
        blank=True,
        help_text="Date the curriculum last verified this resource URL."
    )
    license = models.CharField(
        max_length=128,
        blank=True,
        default='',
        help_text="SPDX-style identifier of the source's licence, e.g. CC-BY-SA-4.0."
    )
    license_url = models.URLField(max_length=500, blank=True, default='')
    license_verified = models.BooleanField(
        default=False,
        help_text="True only once a human has confirmed the licence against the source."
    )
    redistributable = models.BooleanField(
        default=False,
        help_text="Whether the licence permits copying this material into Progressio."
    )
    attribution_required = models.BooleanField(default=True)
    commercial_use_allowed = models.BooleanField(
        default=False,
        help_text="False for non-commercial licences such as CC BY-NC-SA."
    )
    link_status = models.CharField(
        max_length=32,
        blank=True,
        default='',
        help_text="Result of the last reachability check: ok, moved, or broken."
    )
    link_checked_at = models.DateTimeField(null=True, blank=True)
    is_managed = models.BooleanField(
        default=False,
        help_text="True when this record is owned by a curriculum package."
    )

    class Meta:
        db_table = 'lessons'
        ordering = ['skill', 'order']
        constraints = [
            models.UniqueConstraint(
                fields=['skill', 'source_id'],
                condition=models.Q(is_managed=True),
                name='unique_managed_lesson_per_skill_resource',
            )
        ]
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


class StudyStep(TimestampMixin):
    """
    An authored bridge between a source and its assessment.

    The material itself stays at the publisher. A study step points into one
    section of it and states what the learner should do there, which is the part
    Progressio can write without copying anything.
    """
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='study_steps'
    )
    anchor = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Fragment identifying the section to read, e.g. #idempotent_methods."
    )
    prompt = models.TextField(
        help_text="What the learner should do with that section."
    )
    checkpoint_question = models.TextField(
        blank=True,
        default='',
        help_text="Short question to confirm the section was understood."
    )
    checkpoint_answer = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Expected answer. Graded server-side and never serialized."
    )
    estimated_minutes = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'study_steps'
        ordering = ['lesson', 'order']
        unique_together = ('lesson', 'order')
        verbose_name = 'Study Step'
        verbose_name_plural = 'Study Steps'

    def __str__(self):
        return f"{self.lesson.title} step {self.order}"

    @property
    def study_url(self):
        """The source URL, deep-linked to the section this step covers."""
        if self.anchor and not self.anchor.startswith('#'):
            return f"{self.lesson.content_url}#{self.anchor}"
        return f"{self.lesson.content_url}{self.anchor}"
