import uuid
from django.db import models
from django.conf import settings
from apps.common.models import TimestampMixin
from apps.competencies.models import Competency
from apps.assessments.models import Submission


class Credential(TimestampMixin):
    """
    Represents a verified competency credential issued to a student.
    Can be publicly verified by recruiters without authentication.
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ISSUED = 'issued', 'Issued'
        REVOKED = 'revoked', 'Revoked'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique credential identifier."
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credentials'
    )
    competency = models.ForeignKey(
        Competency,
        on_delete=models.CASCADE,
        related_name='credentials'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    score = models.FloatField(
        help_text="Final competency achievement score (0.0 to 100.0)."
    )
    issued_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the credential was officially issued."
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot metadata (student name, competency, track, metrics)."
    )

    class Meta:
        db_table = 'credentials'
        ordering = ['-issued_at', '-created_at']
        verbose_name = 'Credential'
        verbose_name_plural = 'Credentials'

    def __str__(self):
        return f"Credential [{self.id}] - {self.user.username} ({self.competency.title})"

    @property
    def is_valid(self):
        """Returns True if the credential is currently in issued status and not revoked."""
        return self.status == self.Status.ISSUED


class Evidence(TimestampMixin):
    """
    Evidence supporting a verified competency credential (e.g. GitHub repository, demo URL, portfolio file).
    """
    credential = models.ForeignKey(
        Credential,
        on_delete=models.CASCADE,
        related_name='evidences'
    )
    submission = models.ForeignKey(
        Submission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evidences'
    )
    github_url = models.URLField(max_length=500, blank=True, default='')
    file_url = models.URLField(max_length=500, blank=True, default='')
    demo_url = models.URLField(max_length=500, blank=True, default='')
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'credential_evidences'
        ordering = ['-created_at']
        verbose_name = 'Credential Evidence'
        verbose_name_plural = 'Credential Evidences'

    def __str__(self):
        return f"Evidence for Credential [{self.credential_id}]"
