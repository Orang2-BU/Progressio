from django.db import models
from django.conf import settings
from apps.common.models import TimestampMixin
from apps.skills.models import Skill
from apps.careers.models import CareerTrack


class Assessment(TimestampMixin):
    """
    Assessment belongs to one Skill.
    Types: Quiz, Coding Challenge, Mini Project.
    """

    class AssessmentType(models.TextChoices):
        QUIZ = 'quiz', 'Quiz'
        CHALLENGE = 'challenge', 'Challenge'
        PROJECT = 'project', 'Project'

    class EvaluationMode(models.TextChoices):
        RULES = 'rules', 'Rule-based'
        AI = 'ai', 'AI-assisted'

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
    evaluation_mode = models.CharField(
        max_length=20,
        choices=EvaluationMode.choices,
        default=EvaluationMode.RULES,
    )
    grading_config = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Private server-side grading configuration. For quizzes, use "
            "{'answer_key': {'question_id': 'answer'}}. Never expose this field publicly."
        ),
    )

    # --- Curriculum package fields (populated by import_curriculum) ---
    source_id = models.SlugField(
        max_length=255,
        blank=True,
        default='',
        unique=False,
        help_text="Curriculum assessment ID. Empty for hand-authored assessments."
    )
    objective = models.TextField(
        blank=True,
        default='',
        help_text="What this assessment is meant to establish."
    )
    expected_evidence = models.JSONField(
        default=list,
        blank=True,
        help_text="Artifacts a learner must produce, from the curriculum."
    )
    mastery_criteria = models.TextField(
        blank=True,
        default='',
        help_text="Curriculum-defined bar for counting this skill as mastered."
    )
    estimated_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Expected time to complete. Null while the curriculum leaves it undefined."
    )
    is_managed = models.BooleanField(
        default=False,
        help_text="True when this record is owned by a curriculum package."
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


class DiagnosticQuestion(TimestampMixin):
    """A server-graded diagnostic question mapped to one measurable skill."""

    career_track = models.ForeignKey(
        CareerTrack,
        on_delete=models.CASCADE,
        related_name='diagnostic_questions',
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='diagnostic_questions',
    )
    prompt = models.TextField()
    options = models.JSONField(
        default=list,
        help_text="Public answer choices, preferably a list of {value, label} objects.",
    )
    correct_answer = models.CharField(max_length=255)
    explanation = models.TextField(blank=True, default='')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'diagnostic_questions'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.career_track.title}: {self.skill.title} #{self.order}"


class DiagnosticAttempt(TimestampMixin):
    """Immutable result snapshot for a completed diagnostic assessment."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='diagnostic_attempts',
    )
    career_track = models.ForeignKey(
        CareerTrack,
        on_delete=models.CASCADE,
        related_name='diagnostic_attempts',
    )
    answers = models.JSONField(default=dict)
    skill_scores = models.JSONField(default=list)
    weak_skill_ids = models.JSONField(default=list)
    overall_score = models.FloatField(default=0.0)
    completed_at = models.DateTimeField()

    class Meta:
        db_table = 'diagnostic_attempts'
        ordering = ['-completed_at', '-created_at']

    def __str__(self):
        return f"Diagnostic {self.user} - {self.career_track} ({self.overall_score})"
