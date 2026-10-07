from django.utils import timezone
from django.db import connection, transaction
from django.contrib.auth import get_user_model
import os
import hashlib
import json
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
    def issue_credential(cls, user, competency, evidence_data=None, demo=False):
        """Commit the credential and outbox before any provider call."""
        if not demo and connection.in_atomic_block:
            raise RuntimeError('Final issuance cannot run inside an outer database transaction.')
        with transaction.atomic():
            credential = cls._prepare_credential(user, competency, evidence_data, demo)
        if not demo and credential.status not in (Credential.Status.ISSUED, Credential.Status.REVOKED):
            from apps.blockchain.services import BlockchainService
            BlockchainService.record_credential_on_chain(credential)
            credential.refresh_from_db()
        return credential

    @classmethod
    def _prepare_credential(cls, user, competency, evidence_data=None, demo=False):
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

        evidence_data = evidence_data or {}
        passed_submissions = Submission.objects.filter(id__in=eligibility['submission_ids']).select_related('assessment__skill').order_by('assessment__skill_id', 'id')
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

        evidence = [{'submission_id': item.pk,
            'github_url': evidence_data.get('github_url') or item.content.get('github_url', ''),
            'demo_url': evidence_data.get('demo_url') or item.content.get('demo_url', ''),
            'file_url': evidence_data.get('file_url', ''), 'notes': item.feedback}
            for item in passed_submissions]
        identity = {'user': user.pk, 'competency': competency.pk,
            'standard': {k: v for k, v in metadata_snapshot.items() if k not in ('student_name', 'student_email', 'issued_at')},
            'evidence': evidence}
        issuance_key = hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        existing = Credential.objects.filter(issuance_key=issuance_key).first()
        if existing:
            return existing

        credential = Credential.objects.create(
            user=user,
            competency=competency,
            status=Credential.Status.DRAFT if demo else Credential.Status.PENDING,
            score=score,
            issued_at=None,
            metadata=metadata_snapshot,
            issuance_key=issuance_key,
        )

        for item in evidence:
            Evidence.objects.create(credential=credential, **item)
        if demo:
            return credential

        from apps.blockchain.services import BlockchainService
        BlockchainService.prepare_delivery(credential)
        return credential

    @classmethod
    @transaction.atomic
    def revoke_credential(cls, credential_id, reason="Revoked by administrator"):
        """
        Revokes a previously issued credential.
        """
        credential = Credential.objects.select_for_update().get(id=credential_id)
        credential.status = Credential.Status.REVOKED
        credential.metadata['revocation_reason'] = reason
        credential.metadata['revoked_at'] = timezone.now().isoformat()
        credential.save(update_fields=['status', 'metadata', 'updated_at'])
        proof = getattr(credential, 'blockchain_proof', None)
        if proof:
            proof.revoked = True
            proof.save(update_fields=['revoked', 'updated_at'])
        return credential
