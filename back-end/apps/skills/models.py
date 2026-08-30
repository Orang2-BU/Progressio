from django.db import models
from apps.common.models import TimestampMixin
from apps.competencies.models import Competency


class Skill(TimestampMixin):
    """
    Represents a measurable skill inside a competency.
    Examples: JWT, SQL, REST API, Docker
    """

    class Difficulty(models.TextChoices):
        BEGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED = 'advanced', 'Advanced'

    competency = models.ForeignKey(
        Competency,
        on_delete=models.CASCADE,
        related_name='skills'
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, default='')
    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BEGINNER,
    )
    estimated_learning_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Estimated time to learn this skill in minutes."
    )

    class Meta:
        db_table = 'skills'
        ordering = ['competency', 'title']
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'

    def __str__(self):
        return self.title


class SkillPrerequisite(models.Model):
    """
    Defines the Skill Graph — prerequisite relationships between skills.
    Example: REST API → Authentication → Security
    """
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='prerequisites'
    )
    required_skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='required_by'
    )

    class Meta:
        db_table = 'skill_prerequisites'
        unique_together = ('skill', 'required_skill')
        verbose_name = 'Skill Prerequisite'
        verbose_name_plural = 'Skill Prerequisites'

    def __str__(self):
        return f"{self.skill.title} requires {self.required_skill.title}"
