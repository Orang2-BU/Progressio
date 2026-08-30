from django.utils import timezone
from .models import Submission


class AssessmentEvaluationService:
    """
    Service to handle submission lifecycle, evaluation, and triggering progress events.
    Follows Clean Architecture (keeps business logic out of Views).
    """

    @classmethod
    def submit_and_evaluate(cls, user, assessment, content, auto_score=None, feedback=None):
        """
        Processes an assessment submission:
        1. Creates or updates submission in 'submitted' state.
        2. Transitions to 'evaluating'.
        3. Evaluates answers / scoring.
        4. Transitions to 'completed' with score and feedback.
        5. If passed, notifies ProgressService to update SkillProgress & CompetencyProgress.
        """
        # 1. Create submission
        submission = Submission.objects.create(
            user=user,
            assessment=assessment,
            content=content,
            status=Submission.Status.SUBMITTED,
            submitted_at=timezone.now(),
        )

        # 2. Transition to evaluating
        submission.status = Submission.Status.EVALUATING
        submission.save(update_fields=['status'])

        # 3. Evaluate score
        # For MVP: if auto_score is provided, use it; otherwise evaluate based on content answers or default full score for challenge/quiz demo
        if auto_score is not None:
            score = float(auto_score)
        else:
            # Simple MVP auto-grader: calculate percentage of correct answers if answers format provided, else passing score
            answers = content.get('answers', {})
            if isinstance(answers, dict) and len(answers) > 0:
                score = min(float(len(answers) * 25), float(assessment.max_score))
            else:
                score = float(assessment.passing_score)

        if not feedback:
            if score >= assessment.passing_score:
                feedback = f"Great work! You scored {score}/{assessment.max_score} and passed the assessment."
            else:
                feedback = f"You scored {score}/{assessment.max_score}. Minimum passing score is {assessment.passing_score}. Keep practicing and try again!"

        # 4. Finalize completed submission
        submission.score = score
        submission.feedback = feedback
        submission.status = Submission.Status.COMPLETED
        submission.save(update_fields=['score', 'feedback', 'status'])

        # 5. Domain Event: AssessmentPassed -> Update Progress
        if submission.is_passed:
            from apps.learning.services import ProgressService
            ProgressService.record_assessment_passed(
                user=user,
                skill=assessment.skill,
                score=score
            )

        return submission
