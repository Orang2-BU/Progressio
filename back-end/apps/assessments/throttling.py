"""Request budget for the assessment submit endpoint."""
import uuid

from apps.common.throttling import AccountBudget

from .models import Submission


class AssessmentSubmitBudget(AccountBudget):
    """Budget for grading work, counted per authenticated student.

    A retry that carries the ``request_id`` of a submission that already exists
    is not new work: the service returns the stored result without grading or
    rewarding again. Charging for it would punish a client whose response was
    lost in transit, so a known ``request_id`` skips the budget. A request id
    that has never been seen still costs one attempt, which keeps the budget on
    the actual grading work.
    """

    scope = 'expensive_assessment'

    def is_replay(self, request):
        request_id = self.submitted_value(request, 'request_id')
        if not request_id:
            return False
        try:
            request_id = uuid.UUID(request_id)
        except (ValueError, AttributeError, TypeError):
            return False
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            return False
        manager = getattr(Submission, 'objects')
        return manager.filter(user=user, request_id=request_id).exists()
