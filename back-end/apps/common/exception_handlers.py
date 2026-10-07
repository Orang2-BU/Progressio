"""API error handling that keeps retry information in one place."""
import math

from rest_framework.views import exception_handler as drf_exception_handler


def api_exception_handler(exc, context):
    """Add the retry delay of a throttled request to the response body.

    DRF already sets the ``Retry-After`` header for ``429`` responses but leaves
    the machine-readable value only inside the human sentence of ``detail``.
    Echoing it as ``retry_after_seconds``, with the header set from the same
    number, means a client never has to parse prose to schedule its retry.
    """
    response = drf_exception_handler(exc, context)
    wait = getattr(exc, 'wait', None)
    if response is not None and wait is not None and isinstance(response.data, dict):
        seconds = max(1, math.ceil(wait))
        response.data['retry_after_seconds'] = seconds
        response['Retry-After'] = str(seconds)
    return response
