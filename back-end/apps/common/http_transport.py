"""Safe transport helpers for requests carrying provider credentials."""
import ipaddress
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, build_opener


class RedirectRejected(HTTPError):
    """A credentialed provider request attempted to redirect."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def validate_provider_url(url, *, has_credentials):
    """Require HTTPS except unauthenticated loopback development endpoints."""
    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
        port = parsed.port
    except (TypeError, ValueError):
        raise ValueError('Provider URL must be an absolute HTTPS URL.') from None
    if (parsed.scheme not in {'https', 'http'} or not hostname or parsed.username is not None
            or parsed.password is not None or parsed.fragment):
        raise ValueError('Provider URL must be an absolute HTTPS URL without userinfo or fragments.')
    if parsed.scheme == 'https':
        return url
    try:
        loopback = hostname.lower() == 'localhost' or ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        loopback = False
    if has_credentials or not loopback:
        raise ValueError('HTTP provider URLs are allowed only for unauthenticated loopback development.')
    return url


def open_provider_request(request, timeout):
    """Open a request without following redirects, so Authorization cannot hop origins."""
    opener = build_opener(_NoRedirect())
    try:
        return opener.open(request, timeout=timeout)
    except HTTPError as exc:
        if 300 <= exc.code < 400:
            raise RedirectRejected(exc.url, exc.code, 'Provider redirects are not allowed.', exc.hdrs, exc.fp) from None
        raise
