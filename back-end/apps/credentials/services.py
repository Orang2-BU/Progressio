from django.utils import timezone
from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError
from .models import Credential, Evidence
from apps.learning.models import CompetencyProgress
from apps.assessments.models import Submission


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

        has_passed_assessment = Submission.objects.filter(
            user=user,
            assessment__skill__competency=competency,
            status=Submission.Status.COMPLETED,
            score__gte=F('assessment__passing_score'),
        ).exists()
        if not has_passed_assessment:
            return False, progress.score, (
                'A completed, passing assessment is required before a credential can be issued.'
            )

        return True, progress.score, "Eligible for credential issuance."

    @classmethod
    @transaction.atomic
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

        evidence_data = evidence_data or {}
        passed_submissions = Submission.objects.filter(
            user=user,
            assessment__skill__competency=competency,
            status=Submission.Status.COMPLETED,
            score__gte=F('assessment__passing_score'),
        ).order_by('-score', '-submitted_at')
        submission_id = evidence_data.get('submission_id')
        if submission_id:
            submission = passed_submissions.filter(id=submission_id).first()
            if not submission:
                raise ValidationError({
                    'submission_id': (
                        'Evidence must reference your own completed, passing submission '
                        'for this competency.'
                    )
                })
        else:
            submission = passed_submissions.first()

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
            status=Credential.Status.DRAFT,
            score=score,
            issued_at=now,
            metadata=metadata_snapshot
        )

        Evidence.objects.create(
            credential=credential,
            submission=submission,
            github_url=evidence_data.get('github_url', ''),
            file_url=evidence_data.get('file_url', ''),
            demo_url=evidence_data.get('demo_url', ''),
            notes=evidence_data.get('notes', ''),
        )

        # A credential is only issued after a confirmed cryptographic proof exists.
        try:
            from apps.blockchain.services import BlockchainService
            BlockchainService.record_credential_on_chain(credential)
        except Exception as exc:
            raise ValidationError({
                'detail': f'Credential proof could not be anchored: {exc}'
            }) from exc

        credential.status = Credential.Status.ISSUED
        credential.save(update_fields=['status', 'updated_at'])

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
        proof = getattr(credential, 'blockchain_proof', None)
        if proof:
            proof.revoked = True
            proof.save(update_fields=['revoked', 'updated_at'])
        return credential
