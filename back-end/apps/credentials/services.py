from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
import os
from rest_framework.exceptions import ValidationError
from .models import Credential, Evidence
from apps.assessments.models import Submission


class CredentialService:
    """
    Handles business logic for credential eligibility verification and issuance.
    """

    @classmethod
    def eligibility(cls, user, competency):
        skills = list(competency.skills.order_by('id'))
        submissions = Submission.objects.filter(user=user, assessment__skill__competency=competency,
            status=Submission.Status.COMPLETED).select_related('assessment').order_by('-score', '-id')
        selected = {}
        for submission in submissions:
            snapshot = submission.evaluation
            if (snapshot.get('max_score', 0) > 0 and submission.score is not None and
                    submission.score >= snapshot.get('passing_score', float('inf')) and
                    snapshot.get('curriculum_version') == competency.career_track.curriculum_version):
                previous = selected.get(submission.assessment.skill_id)
                def rank(s):
                    return (s.evaluation.get('review_status') == 'reviewed' and s.evaluation.get('provider') in ('rules', 'openai'),
                        s.score / s.evaluation['max_score'], s.pk)
                if previous is None or rank(submission) > rank(previous):
                    selected[submission.assessment.skill_id] = submission
        missing = [{'id': skill.id, 'title': skill.title} for skill in skills if skill.id not in selected]
        ready = bool(skills) and not missing
        final = ready and competency.career_track.is_active and bool(competency.career_track.curriculum_version) and competency.career_track.curriculum_schema_version > 0 and competency.career_track.metadata.get('status') == 'reviewed' and all(
            s.evaluation.get('review_status') == 'reviewed' and s.evaluation.get('provider') in ('rules', 'openai')
            for s in selected.values()) and os.getenv('BLOCKCHAIN_PROVIDER', 'mock').lower() == 'http'
        reason = ('Eligible for final issuance.' if final else
            'Demo only: reviewed curriculum, reviewed non-mock evidence and a live proof provider are required.' if ready else
            'A completed passing assessment for every required skill and current curriculum version is required.')
        return {'competency': competency.id, 'career_track': competency.career_track_id, 'eligible': final, 'demo_ready': ready, 'reason': reason,
            'missing_skills': missing, 'submission_ids': [selected[s.id].id for s in skills if s.id in selected],
            'score': round(sum(selected[s.id].score / selected[s.id].evaluation['max_score'] * 100 for s in skills if s.id in selected) / len(skills), 1) if skills else 0,
            'curriculum_version': competency.career_track.curriculum_version,
            'curriculum_status': competency.career_track.metadata.get('status', 'unreviewed'),
            'proof_provider': os.getenv('BLOCKCHAIN_PROVIDER', 'mock').lower()}

    @classmethod
    def check_eligibility(cls, user, competency):
        """
        Compatibility tuple for callers; eligibility is based on assessment evidence.
        """
        result = cls.eligibility(user, competency)
        return result['eligible'], result['score'], result['reason']

    @classmethod
    @transaction.atomic
    def issue_credential(cls, user, competency, evidence_data=None, demo=False):
        """
        Issues a new verified credential for the user:
        1. Checks eligibility.
        2. Creates Credential record with snapshot metadata.
        3. Attaches Evidence if provided.
        """
        get_user_model().objects.select_for_update().get(pk=user.pk)
        eligibility = cls.eligibility(user, competency)
        if not eligibility['eligible'] and not (demo and eligibility['demo_ready']):
            raise ValidationError({'detail': eligibility['reason']})
        score = eligibility['score']

        # Check if already issued
        existing = Credential.objects.filter(
            user=user,
            competency=competency,
            status=Credential.Status.DRAFT if demo else Credential.Status.ISSUED,
            metadata__curriculum_version=competency.career_track.curriculum_version,
            metadata__submission_ids=eligibility['submission_ids'],
        ).first()
        if existing:
            return existing

        evidence_data = evidence_data or {}
        passed_submissions = Submission.objects.filter(id__in=eligibility['submission_ids']).select_related('assessment')
        submission_id = evidence_data.get('submission_id')
        if submission_id:
            if not passed_submissions.filter(id=submission_id).exists():
                raise ValidationError({
                    'submission_id': (
                        'Evidence must reference your own completed, passing submission '
                        'for this competency.'
                    )
                })

        now = timezone.now()
        track = competency.career_track
        metadata_snapshot = {
            'student_name': user.get_full_name() or user.username,
            'student_email': user.email,
            'competency_id': competency.slug,
            'competency_title': competency.title,
            'career_track_id': track.slug if track else '',
            'career_track_title': track.title if track else '',
            # Pin the standard this credential was graded against, so the claim
            # stays interpretable after the curriculum moves on.
            'curriculum_version': track.curriculum_version if track else '',
            'curriculum_schema_version': track.curriculum_schema_version if track else 0,
            'observable_behaviors': competency.observable_behaviors,
            'score': score,
            'issued_at': None if demo else now.isoformat(),
            'mode': 'demo' if demo else 'final',
            'proof_provider': 'none' if demo else 'http',
            'submission_ids': eligibility['submission_ids'],
            'skill_standards': [{'skill_id': s.assessment.skill_id, 'title': s.assessment.skill.title,
                'evaluation': s.evaluation, 'score': s.score} for s in passed_submissions],
        }

        credential = Credential.objects.create(
            user=user,
            competency=competency,
            status=Credential.Status.DRAFT,
            score=score,
            issued_at=None if demo else now,
            metadata=metadata_snapshot
        )

        for item in passed_submissions:
            Evidence.objects.create(credential=credential, submission=item,
                github_url=evidence_data.get('github_url') or item.content.get('github_url', ''),
                demo_url=evidence_data.get('demo_url') or item.content.get('demo_url', ''),
                file_url=evidence_data.get('file_url', ''),
                notes=item.feedback)
        if demo:
            return credential

        # A credential is only issued after a confirmed cryptographic proof exists.
        try:
            from apps.blockchain.services import BlockchainService
            BlockchainService.record_credential_on_chain(credential)
        except Exception as exc:
            raise ValidationError({
                'detail': 'Credential proof could not be confirmed; no credential was issued.'
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
