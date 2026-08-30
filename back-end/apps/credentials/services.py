from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .models import Credential, Evidence
from apps.learning.models import CompetencyProgress


class CredentialService:
    """
    Handles business logic for credential eligibility verification and issuance.
    """

    MINIMUM_ELIGIBILITY_SCORE = 70.0

    @classmethod
    def check_eligibility(cls, user, competency):
        """
        Verifies if user meets minimum score threshold (>=70%) to earn a credential.
        """
        progress = CompetencyProgress.objects.filter(
            user=user,
            competency=competency
        ).first()

        if not progress:
            return False, 0.0, f"No learning progress found for competency '{competency.title}'."

        if progress.score < cls.MINIMUM_ELIGIBILITY_SCORE:
            return False, progress.score, (
                f"Competency score is {progress.score}%. "
                f"Minimum required score to earn a credential is {cls.MINIMUM_ELIGIBILITY_SCORE}%."
            )

        return True, progress.score, "Eligible for credential issuance."

    @classmethod
    def issue_credential(cls, user, competency, evidence_data=None):
        """
        Issues a new verified credential for the user:
        1. Checks eligibility.
        2. Creates Credential record with snapshot metadata.
        3. Attaches Evidence if provided.
        """
        is_eligible, score, reason = cls.check_eligibility(user, competency)
        if not is_eligible:
            raise ValidationError({'detail': reason})

        # Check if already issued
        existing = Credential.objects.filter(
            user=user,
            competency=competency,
            status=Credential.Status.ISSUED
        ).first()
        if existing:
            return existing

        now = timezone.now()
        metadata_snapshot = {
            'student_name': user.get_full_name() or user.username,
            'student_email': user.email,
            'competency_title': competency.title,
            'career_track_title': competency.career_track.title if competency.career_track else '',
            'score': score,
            'issued_at': now.isoformat(),
        }

        credential = Credential.objects.create(
            user=user,
            competency=competency,
            status=Credential.Status.ISSUED,
            score=score,
            issued_at=now,
            metadata=metadata_snapshot
        )

        # Attach evidence if provided
        if evidence_data:
            Evidence.objects.create(
                credential=credential,
                submission_id=evidence_data.get('submission_id'),
                github_url=evidence_data.get('github_url', ''),
                file_url=evidence_data.get('file_url', ''),
                demo_url=evidence_data.get('demo_url', ''),
                notes=evidence_data.get('notes', ''),
            )

        return credential

    @classmethod
    def revoke_credential(cls, credential_id, reason="Revoked by administrator"):
        """
        Revokes a previously issued credential.
        """
        credential = Credential.objects.get(id=credential_id)
        credential.status = Credential.Status.REVOKED
        credential.metadata['revocation_reason'] = reason
        credential.metadata['revoked_at'] = timezone.now().isoformat()
        credential.save(update_fields=['status', 'metadata', 'updated_at'])
        return credential
