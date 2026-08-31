from celery import shared_task
from apps.assessments.models import Submission
from apps.learning.services import ProgressService
from .services import AIService


@shared_task(name="apps.ai.tasks.evaluate_submission_ai_task")
def evaluate_submission_ai_task(submission_id):
    """
    Celery background worker task to perform AI-assisted evaluation on a submission.
    """
    try:
        submission = Submission.objects.select_related('assessment').get(id=submission_id)
        if submission.status == Submission.Status.COMPLETED:
            return f"Submission {submission_id} was already evaluated"
        submission.status = Submission.Status.EVALUATING
        submission.save(update_fields=['status'])
        adapter = AIService.get_adapter()
        evaluation = adapter.evaluate_submission(
            assessment=submission.assessment,
            submission_content=submission.content
        )

        submission.feedback = evaluation.get('feedback', submission.feedback)
        if evaluation.get('score') is not None:
            submission.score = evaluation['score']
        submission.status = Submission.Status.COMPLETED
        submission.save(update_fields=['score', 'feedback', 'status'])
        if submission.is_passed:
            ProgressService.record_assessment_passed(
                user=submission.user,
                skill=submission.assessment.skill,
                score=submission.score,
            )
        return f"Submission {submission_id} evaluated with score {submission.score}"
    except Submission.DoesNotExist:
        return f"Submission {submission_id} not found"
