from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.assessments.models import Submission
from apps.assessments.services import AssessmentEvaluationService
from .services import AIService


@shared_task(name="apps.ai.tasks.evaluate_submission_ai_task")
def evaluate_submission_ai_task(submission_id):
    """
    Celery background worker task to perform AI-assisted evaluation on a submission.
    """
    try:
        submission_ref = Submission.objects.only('user_id').get(id=submission_id)
        with transaction.atomic():
            get_user_model().objects.select_for_update().get(pk=submission_ref.user_id)
            submission = Submission.objects.select_for_update().select_related(
                'assessment'
            ).get(id=submission_id)
            if submission.status == Submission.Status.COMPLETED:
                return f"Submission {submission_id} was already evaluated"
            if submission.status != Submission.Status.EVALUATING:
                submission.status = Submission.Status.EVALUATING
                submission.save(update_fields=['status'])

        adapter = AIService.get_adapter()
        evaluation = adapter.evaluate_submission(
            assessment=submission.assessment,
            submission_content=submission.content
        )
        submission = AssessmentEvaluationService.complete_evaluation(
            submission_id, evaluation
        )
        return f"Submission {submission_id} evaluated with score {submission.score}"
    except Submission.DoesNotExist:
        return f"Submission {submission_id} not found"
