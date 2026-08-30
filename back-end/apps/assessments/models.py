from django.db import models
from django.conf import settings
from apps.common.models import TimestampMixin
from apps.skills.models import Skill


class Assessment(TimestampMixin):
    """
    Assessment belongs to one Skill.
    Types: Quiz, Coding Challenge, Mini Project.
    """

    class AssessmentType(models.TextChoices):
        QUIZ = 'quiz', 'Quiz'
        CHALLENGE = 'challenge', 'Challenge'
        PROJECT = 'project', 'Project'

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='assessments'
    )
    title = models.CharField(max_length=255)
    assessment_type = models.CharField(
        max_length=20,
        choices=AssessmentType.choices,
        default=AssessmentType.QUIZ,
    )
    instructions = models.TextField(blank=True, default='')
    passing_score = models.PositiveIntegerField(
        default=70,
        help_text="Minimum score required to pass."
    )
    max_score = models.PositiveIntegerField(
        default=100,
        help_text="Maximum possible score."
    )

    class Meta:
        db_table = 'assessments'
        ordering = ['skill', 'title']
        verbose_name = 'Assessment'
        verbose_name_plural = 'Assessments'

    def __str__(self):
        return f"{self.title} ({self.get_assessment_type_display()})"


class Submission(TimestampMixin):
    """
    Student submission for an Assessment.
    Implements state machine: draft -> submitted -> evaluating -> completed.
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SUBMITTED = 'submitted', 'Submitted'
        EVALUATING = 'evaluating', 'Evaluating'
        COMPLETED = 'completed', 'Completed'

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    content = models.JSONField(
        default=dict,
        blank=True,
        help_text="Submission payload, answers, code, or repository metadata."
    )
    score = models.FloatField(
        null=True,
        blank=True,
        help_text="Awarded score from 0 to max_score."
    )
    feedback = models.TextField(
        blank=True,
        default='',
        help_text="Automated or evaluator feedback."
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when submission was finalized."
    )

    class Meta:
        db_table = 'submissions'
        ordering = ['-created_at']
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'

    def __str__(self):
        return f"Submission by {self.user} for {self.assessment.title} [{self.status}]"

    @property
    def is_passed(self):
        """Returns True if submission scored >= assessment passing_score."""
        if self.score is not None and self.assessment is not None:
            return self.score >= self.assessment.passing_score
        return False
