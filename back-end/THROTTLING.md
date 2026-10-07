# API request budgets

The API uses DRF throttles for registration, login, token refresh, assessment
submission, AI analysis/recommendations, credential issuance, and public
credential verification. Defaults are deliberately modest starting points, not
capacity guarantees: `60/hour` registrations per client address, `10/min` login
attempts per attempted account and client address plus `60/min` aggregate login
attempts per client address, `30/min` refreshes per
address, `30/hour` assessments per account, `20/hour` AI requests per account,
`10/hour` credential issues per account, and `60/min` public verifications per
address. Tune these values against observed usage and provider quotas.

Each value can be changed with `THROTTLE_RATE_AUTH_REGISTER`,
`THROTTLE_RATE_AUTH_LOGIN`, `THROTTLE_RATE_AUTH_LOGIN_IP`,
`THROTTLE_RATE_AUTH_REFRESH`,
`THROTTLE_RATE_ASSESSMENT_SUBMIT`, `THROTTLE_RATE_AI`,
`THROTTLE_RATE_CREDENTIAL_ISSUE`, and `THROTTLE_RATE_PUBLIC_VERIFY`. Values
use `<count>/<second|minute|hour|day>` (for example, `10/min`). A rejected
request returns HTTP 429, with the same whole-second delay in `Retry-After`
and `retry_after_seconds`.

## Cache and deployment

Every web process must use the same Redis cache for shared hosted budgets. A
deployment with `DEBUG=False` fails during settings import if it has no shared
Redis throttle cache configured. Set
`THROTTLE_CACHE_URL=redis://<redis-host>:6379/1` on every web instance. If that
is unset, a Redis `CELERY_BROKER_URL` is reused; otherwise Django's local-memory
cache is used, which means each process has independent counters and the
effective limit can multiply by the number of processes. Do not use local
memory for a multi-process hosted deployment. Configure the cache URL and
`THROTTLE_CACHE_KEY_PREFIX` consistently across instances; use a dedicated
Redis database or prefix to avoid collisions.

DRF's rolling-window throttle performs cache reads and writes rather than an
atomic increment/compare operation. Concurrent requests can therefore exceed a
limit briefly. These controls reduce application-level bursts and repeated
expensive work; they are not complete DDoS protection. Apply volumetric and
coarse per-IP limits at a CDN, load balancer, or reverse proxy as appropriate.

## Client IP and proxies

By default, throttles use `REMOTE_ADDR` and ignore `X-Forwarded-For`. Set
`TRUSTED_PROXY_COUNT` to the number of trusted proxies only when the final edge
proxy removes any client-supplied forwarded header and writes the forwarding
chain itself. The application selects the address at that configured depth;
if the chain is shorter than configured, it falls back to `REMOTE_ADDR`. Never
trust a forwarded header from a directly reachable client. Login account names
are HMAC-digested in cache identities; passwords and access/refresh tokens are
never included in throttle keys or logs.

## Idempotent assessment retries

An assessment submission with a previously completed `request_id` is allowed
through the throttle so a client can recover a lost response. The service
returns the stored submission and does not evaluate or award progress twice.
New request IDs still spend the assessment budget.
