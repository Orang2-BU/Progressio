"""Per-request budgets for credential attempts and for costly operations.

Two families are kept apart on purpose:

``auth_*``
    Unauthenticated attempts against register/login/refresh. A guesser picks a
    new username every time, so these budgets are counted per client address and
    -- for login -- per attempted username as well.

``expensive_*`` and ``public_verify``
    Endpoints that can reach an external provider (OpenAI, an on-chain signer)
    or run a whole grading pass. These are counted per authenticated account so
    one noisy client cannot spend another student's provider budget.

What this does and does not guarantee:

* A request over budget gets ``429`` with the same number of seconds in the
  ``Retry-After`` header and in the ``retry_after_seconds`` body field.
* Counters live in the dedicated ``THROTTLE_CACHE_ALIAS`` cache, so every
  process of a hosted deployment shares one budget. With no shared cache the
  counters are per process and the effective limit is ``limit x processes``.
* Counting is a cache read followed by a cache write, not a compare-and-swap,
  so requests landing in the same instant can overshoot the budget by roughly
  the number of in-flight requests. This guards against runaway clients and
  credential guessing at the application layer; it is not volumetric DDoS
  protection and does not replace edge limits. See ``back-end/THROTTLING.md``.
* No secret reaches a cache key: passwords and refresh tokens are never part of
  the identity, and an attempted username is stored as an HMAC digest so a
  cache dump does not enumerate account names.
"""
import hashlib
import hmac
import logging
import re
import time

from django.conf import settings
from django.core.cache import caches
from django.core.exceptions import ImproperlyConfigured
from rest_framework.throttling import SimpleRateThrottle

logger = logging.getLogger(__name__)

# Used when a request carries no address we can attribute at all.
UNKNOWN_CLIENT = 'unknown'
# Digest length kept short so a cache key stays readable in a Redis listing.
DIGEST_LENGTH = 32
# Upper bound on the attempt value that feeds the digest.
ATTEMPT_LENGTH = 150
# Characters an address may contain; anything else is dropped so a forged
# header cannot smuggle whitespace or control characters into keys or logs.
ADDRESS_ALLOWED = re.compile(r'[^0-9a-zA-Z:.%-]')


def now():
    """Clock seam so tests can advance time without patching ``time``."""
    return time.time()


def normalise_address(value):
    """Reduce an address to a short, key- and log-safe token."""
    return ADDRESS_ALLOWED.sub('', (value or '').strip())[:64] or UNKNOWN_CLIENT


def client_address(request):
    """Return the client address, trusting ``X-Forwarded-For`` only if configured.

    DRF's own ``SimpleRateThrottle.get_ident`` folds the entire
    ``X-Forwarded-For`` header into the identity when no proxy depth is set, so
    a client that edits the header gets a fresh budget on every request. Here
    the header is ignored unless ``TRUSTED_PROXY_COUNT`` declares how many
    proxies sit in front of the application, and the edge proxy has to replace
    the inbound header instead of appending to it.
    """
    remote_addr = normalise_address(request.META.get('REMOTE_ADDR'))
    if remote_addr == UNKNOWN_CLIENT:
        return UNKNOWN_CLIENT
    trusted_proxies = getattr(settings, 'TRUSTED_PROXY_COUNT', 0) or 0
    if trusted_proxies < 1:
        return remote_addr
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR') or ''
    addresses = [item.strip() for item in forwarded.split(',') if item.strip()]
    if len(addresses) < trusted_proxies:
        # Shorter than the configured chain, so it was forged or a hop is not
        # appending. The peer's own address is the only claim we can trust.
        return remote_addr
    return normalise_address(addresses[len(addresses) - trusted_proxies])


def digest(value):
    """Key-safe, non-reversible stand-in for a value we must not store."""
    secret = str(getattr(settings, 'SECRET_KEY', '') or 'progressio').encode('utf-8')
    return hmac.new(secret, value.encode('utf-8'), hashlib.sha256).hexdigest()[:DIGEST_LENGTH]


class BudgetThrottle(SimpleRateThrottle):
    """``SimpleRateThrottle`` counting into the shared throttle cache.

    Rates come from the ``THROTTLE_RATES`` setting rather than DRF's frozen
    ``DEFAULT_THROTTLE_RATES`` snapshot so a deployment -- or a test -- can
    repoint a single scope through ``override_settings``.
    """

    @property
    def cache(self):
        # Resolved per request so tests and deployments can repoint the alias.
        return caches[getattr(settings, 'THROTTLE_CACHE_ALIAS', 'default')]

    @staticmethod
    def timer():
        return now()

    def get_rate(self):
        rates = getattr(settings, 'THROTTLE_RATES', {}) or {}
        rate = rates.get(self.scope)
        if not rate:
            raise ImproperlyConfigured(
                f"No request budget configured for throttle scope '{self.scope}'."
            )
        return rate

    def identity(self, request):
        raise NotImplementedError

    def is_replay(self, request):
        """Return True when the payload only asks for an earlier result.

        DRF throttles before the handler runs, so a client retrying a write
        whose response it never received would pay twice for work already
        stored. An endpoint whose write is idempotent can override this to let
        the replay through; the handler still refuses to grade or reward twice.
        """
        return False

    def get_cache_key(self, request, view):
        if self.is_replay(request):
            return None
        identity = self.identity(request)
        if not identity:
            return None
        return self.cache_format % {'scope': self.scope, 'ident': identity}

    @staticmethod
    def submitted_value(request, field):
        """Read one scalar field from the request body, tolerating any shape."""
        try:
            data = request.data
        except Exception:  # unparseable, streamed, or absent body
            return None
        if not isinstance(data, dict):
            return None
        value = data.get(field)
        if isinstance(value, (list, tuple)):  # a repeated form field
            value = value[0] if value else None
        if not isinstance(value, str):
            return None
        return value.strip()[:ATTEMPT_LENGTH]


class ClientAddressBudget(BudgetThrottle):
    """Budget counted per client address."""

    def identity(self, request):
        return f'ip:{client_address(request)}'


class AccountAttemptBudget(ClientAddressBudget):
    """Budget counted per attempted account and client address.

    Counting both keeps one student's mistyped password from spending another
    student's budget behind the same campus NAT, while still capping how often
    one account can be guessed from one address. The attempted account name is
    only ever stored as a digest.
    """

    attempt_field = 'username'

    def identity(self, request):
        attempt = self.submitted_value(request, self.attempt_field)
        if not attempt:
            # No usable account name in the body: fall back to the address
            # alone instead of pooling every malformed attempt together.
            return super().identity(request)
        return f'account:{digest(attempt.casefold())}@{client_address(request)}'


class AccountBudget(BudgetThrottle):
    """Budget counted per authenticated account, falling back to the address."""

    def identity(self, request):
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            return f'user:{user.pk}'
        return f'ip:{client_address(request)}'


class AuthRegisterThrottle(ClientAddressBudget):
    """Registration is cheap, but a burst of it is account spam."""

    scope = 'auth_register'


class AuthLoginThrottle(AccountAttemptBudget):
    """Counts attempts against one account and source address."""

    scope = 'auth_login'


class AuthLoginAddressThrottle(ClientAddressBudget):
    """Also cap aggregate login attempts from one source address."""

    scope = 'auth_login_ip'


class AuthRefreshThrottle(ClientAddressBudget):
    """Refresh tokens are bearer material, so the key is the address only.

    The token itself is never part of the identity: putting a hash of it in the
    key would still let anyone holding one token mint a separate budget.
    """

    scope = 'auth_refresh'


class AiServiceBudget(AccountBudget):
    """AI endpoints can call a billed provider."""

    scope = 'expensive_ai'


class CredentialIssueBudget(AccountBudget):
    """Issuing a credential publishes an external proof."""

    scope = 'expensive_credential'


class PublicVerifyBudget(ClientAddressBudget):
    """Public verification re-derives the hash and may call the proof provider."""

    scope = 'public_verify'
