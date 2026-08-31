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


def check_url(url):
    """Return one of 'ok', 'moved', or 'broken' for a single URL."""
    if not url:
        return 'broken'

    request = urllib.request.Request(url, method='HEAD', headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            if response.url.rstrip('/') != url.rstrip('/'):
                return 'moved'
            return 'ok'
    except urllib.error.HTTPError as error:
        # Some publishers reject HEAD but serve GET perfectly well.
        if error.code in (403, 405):
            return 'ok'
        return 'broken'
    except (urllib.error.URLError, ValueError, OSError):
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
