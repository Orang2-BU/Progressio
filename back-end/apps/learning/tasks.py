"""
Reachability checks for the sources the curriculum points at.

Progressio links to material rather than copying it, so a dead link is a real
defect in the product. This only requests headers — no content is fetched,
stored, or derived — which keeps the check clear of every licence question.
"""
import logging
import urllib.error
import urllib.request

from celery import shared_task
from django.utils import timezone

from .models import Lesson

logger = logging.getLogger(__name__)

USER_AGENT = 'ProgressioLinkCheck/1.0 (+https://github.com/Orang2-BU/Progressio)'
TIMEOUT_SECONDS = 15


def _status_for_final_url(url, final_url):
    """Map a resolved final URL to 'ok' or 'moved' without reading any body."""
    if final_url.rstrip('/') != url.rstrip('/'):
        return 'moved'
    return 'ok'


def _open_without_body(request):
    """
    Open a URL and classify it by its final URL only.

    The response is closed immediately by the caller via the context
    manager; the body is never read, stored, or derived from.
    """
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return _status_for_final_url(request.full_url, response.url)


def _close_error_without_reading(error):
    """
    Close an HTTPError response stream immediately without reading it.

    urlopen raises HTTPError carrying the live response; classifying the
    status without closing leaks the stream. Never call read() here — the
    link check must not fetch publisher content.
    """
    try:
        error.close()
    except Exception:  # pragma: no cover - close must never break classification
        logger.debug('Failed to close HTTPError stream', exc_info=True)


def check_url(url):
    """Return one of 'ok', 'moved', or 'broken' for a single URL."""
    if not url:
        return 'broken'

    head_request = urllib.request.Request(url, method='HEAD', headers={'User-Agent': USER_AGENT})
    try:
        return _open_without_body(head_request)
    except urllib.error.HTTPError as error:
        # Close the HEAD error stream before doing anything else — in
        # particular before starting the fallback GET. Some publishers
        # reject HEAD but serve GET perfectly well, so a 403/405 to HEAD
        # alone proves nothing about reachability. Any other HEAD status
        # (404, 5xx, ...) is a real signal: broken.
        _close_error_without_reading(error)
        if error.code not in (403, 405):
            return 'broken'
    except (urllib.error.URLError, ValueError, OSError):
        return 'broken'

    get_request = urllib.request.Request(url, method='GET', headers={'User-Agent': USER_AGENT})
    try:
        return _open_without_body(get_request)
    except urllib.error.HTTPError as error:
        # Close the denied GET stream without reading it: a GET denial,
        # bot-block, or rate-limit proves nothing except "not confirmed".
        _close_error_without_reading(error)
        return 'broken'
    except (urllib.error.URLError, ValueError, OSError):
        # Redirect loop, timeout, DNS failure, or bot-block: none of these
        # prove the learner can open the link.
        return 'broken'


@shared_task(name='learning.check_resource_links')
def check_resource_links():
    """
    Refresh link_status for every curriculum-managed lesson.

    Returns a summary rather than mutating curriculum files: a dead link is a
    curriculum decision, so this reports and a human updates the package.
    """
    summary = {'ok': 0, 'moved': 0, 'broken': 0}
    checked_at = timezone.now()

    for lesson in Lesson.objects.filter(is_managed=True).order_by('id'):
        result = check_url(lesson.content_url)
        summary[result] += 1
        lesson.link_status = result
        lesson.link_checked_at = checked_at
        lesson.save(update_fields=['link_status', 'link_checked_at', 'updated_at'])
        if result != 'ok':
            logger.warning(
                'Curriculum resource %s is %s: %s', lesson.source_id, result, lesson.content_url
            )

    return summary
