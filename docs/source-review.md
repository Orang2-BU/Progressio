# Source review — backend-engineering resources (plan 004)

Date of review: 2026-10-05. Package state: all 13 resources declare
`license_verified: false`; **no resource file was changed by this review**
because no content-specific publisher evidence was established
(`rg -n 'license_verified' curriculum/tracks/backend-engineering/resources`
still shows `false` on all 13 files).

## What this document is (and is not)

- **Link access** (can a learner open the URL?) is reported from
  `python manage.py check_links` runs below. It says nothing about reuse rights.
- **Reuse permission** (may Progressio copy/redistribute the material?) is
  **unverified for every resource**. The `license` / `license_url` values in
  the package are package-declared claims pointing at the publisher's
  *generic* license page. Per plan 004, a generic license page is not
  content-specific evidence, so nothing was flipped to `license_verified: true`.
- Progressio links to these sources; it does not copy them. No publisher
  material was fetched, stored, or republished during this review. The link
  checker requests headers only (HEAD, with a bounded header-only GET fallback
  for HEAD 403/405) and never reads the response body.
- One audit run is not a verdict: a single non-OK result is recorded as-is
  with its context, not as proof a source is dead.

## Link-check runs (disposable persistent SQLite DB)

Both runs used the same DB settings: `$env:DB_ENGINE = "sqlite"` against a
freshly migrated file DB (`back-end/db.sqlite3`, gitignored, created for this
review via `migrate --run-syncdb` + `import_curriculum --track
backend-engineering`), so the `check_links` process inspected the exact DB it
reported on — never an assumed shared in-memory SQLite.

- Run 1, 2026-10-05: `ok=16 moved=0 broken=1` —
  `broken: mdn-client-server -> https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/First_steps/Client-Server_overview`.
- Manual re-probe immediately after (same UA `ProgressioLinkCheck/1.0`, HEAD
  and GET): `HEAD OK 200`, `GET OK 200`, final URL unchanged. A browser-UA
  fetch of the same URL also rendered the full "Client-server overview" page.
- Run 2, 2026-10-05: `ok=17 moved=0 broken=0` — "All curriculum links reachable."

Conclusion on access: all 13 resource URLs (17 managed lessons — some
resources back more than one skill) are reachable as of 2026-10-05. The single
`broken` in run 1 is assessed as **transient** (rate-limit / transient 5xx
during a 17-request batch, consistent with the transient 503 noted in plan
004), not a dead link. Recheck shortly before presenting, as link health drifts.

## Per-resource rows

| # | Resource ID | Source URL | Access (2026-10-05) | Declared license (package) | Publisher license evidence | Verified for this specific content? | Reuse / attribution notes | Uncertainty |
|---|-------------|------------|---------------------|----------------------------|----------------------------|-------------------------------------|---------------------------|-------------|
| 1 | `exercism-python` | https://exercism.org/tracks/python/exercises | ok (`check_links` run 2; 17/17 ok) | Proprietary; `license_url`: https://exercism.org/terms-of-service | Package-declared only; publisher ToS page cited but not content-checked | No — `license_verified` stays `false` | `redistributable: false`, commercial use not allowed; link-only use | Exercism mixes platform, mentor, and user-contributed exercise content, so rights are ambiguous per contributor; never infer redistribution rights from HTTP success |
| 2 | `mdn-client-server` | https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/First_steps/Client-Server_overview | ok on run 2; **transient `broken` on run 1**, manual HEAD+GET re-probe `200`, browser fetch rendered page | CC-BY-SA-2.5; `license_url`: MDN copyright/attribution page | Package-declared only; MDN's generic licensing page cited but not content-checked | No — `license_verified` stays `false` | Attribution required; do not copy article text into Progressio without content-specific confirmation (MDN also licenses code examples separately) | Transient run-1 failure shows automated checks can flake; MDN restructures Learn content periodically, so recheck before demo |
| 3 | `mdn-http-messages` | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages | ok (`check_links` run 2) | CC-BY-SA-2.5; MDN copyright page | Package-declared only, generic page | No — stays `false` | Attribution required; link-only | Same MDN caveats as above |
| 4 | `mdn-http-methods` | https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods | ok (`check_links` run 2) | CC-BY-SA-2.5; MDN copyright page | Package-declared only, generic page | No — stays `false` | Attribution required; link-only | Same MDN caveats as above |
| 5 | `mdn-http-overview` | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | ok (`check_links` run 2) | CC-BY-SA-2.5; MDN copyright page | Package-declared only, generic page | No — stays `false` | Attribution required; link-only | Same MDN caveats as above |
| 6 | `mdn-http-status` | https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status | ok (`check_links` run 2) | CC-BY-SA-2.5; MDN copyright page | Package-declared only, generic page | No — stays `false` | Attribution required; link-only | Same MDN caveats as above |
| 7 | `openapi-spec` | https://spec.openapis.org/oas/ | ok (`check_links` run 2) | Apache-2.0; `license_url`: https://www.apache.org/licenses/LICENSE-2.0 | Package-declared only; Apache license text is generic, not a per-page grant | No — stays `false` | Attribution required; link-only; spec text reuse needs initiative's terms, not just the Apache text | Specification site is versioned; confirm the exact version URL before presenting |
| 8 | `owasp-input-validation` | https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html | ok (`check_links` run 2) | CC-BY-SA-4.0; `license_url`: https://creativecommons.org/licenses/by-sa/4.0/ | Package-declared only; CC deed is generic, not per-page evidence | No — stays `false` | Attribution + share-alike required if ever reused; link-only for now | Cheat-sheet series accepts community contributions; per-page provenance not checked |
| 9 | `pro-git-basics` | https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository.html | ok (`check_links` run 2) | CC-BY-NC-SA-3.0; `license_url`: https://creativecommons.org/licenses/by-nc-sa/3.0/ | Package-declared only, generic deed | No — stays `false` | **Non-commercial**: `redistributable: false`, `commercial_use_allowed: false` already correct; link-only, attribution required | NC clause rules out copying into any commercial offering; no change needed, no upgrade claimed |
| 10 | `pro-git-recording` | https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository | ok (`check_links` run 2) | CC-BY-NC-SA-3.0; CC BY-NC-SA 3.0 deed | Package-declared only, generic deed | No — stays `false` | Same NC restriction as above; link-only | Same as above |
| 11 | `python-control-flow` | https://docs.python.org/3/tutorial/controlflow.html | ok (`check_links` run 2; earlier transient-503 history noted in plan 004 judged inconclusive) | PSF-2.0; `license_url`: https://docs.python.org/3/license.html | Package-declared only; PSF license page is generic | No — stays `false` | Attribution required; link-only; docs.python.org version path (`/3/`) floats, so pin version before presenting | Prior 503 was transient; this run is ok, but floating `/3/` URL can change meaning across releases |
| 12 | `python-tutorial` | https://docs.python.org/3/tutorial/index.html | ok (`check_links` run 2) | PSF-2.0; https://docs.python.org/3/license.html | Package-declared only, generic page | No — stays `false` | Same as above; link-only | Same floating-version caveat as above |
| 13 | `rfc-9110` | https://www.rfc-editor.org/rfc/rfc9110.html | ok (`check_links` run 2) | IETF-Trust; `license_url`: https://trustee.ietf.org/documents/trust-legal-provisions/ | Package-declared only; Trust provisions are generic, with separate rules for code components | No — stays `false` | Attribution required; link-only; RFC text has excerpt/republication limits beyond a plain open license | Standards-track metadata (obsoleted-by / updated-by) should be glanced at before presenting |

## Decisions

- **No resource YAML changed.** Every `license_verified` remains `false`
  because no content-specific publisher evidence was gathered — only
  package-declared claims against generic license pages, which plan 004
  explicitly excludes as verification basis.
- **No URL changed.** All URLs resolve as of 2026-10-05 (run 2: 17/17 ok);
  the run-1 `mdn-client-server` blip was proven transient by immediate
  re-probe, so no curriculum edit was warranted.
- **No bot-blocked host needed an `unconfirmed` access verdict this time:**
  both HEAD and GET with the product UA returned 200 on direct re-probe, and
  the batch re-run confirmed 17/17 ok. If a future run shows a publisher
  blocking automated checks (403/405 on both HEAD and GET, 429, CAPTCHA),
  record that resource's access as `unconfirmed` rather than `ok` and do not
  flip any license flag.

## Maintenance

Link health changes over time; rerun `check_links` against a disposable
persistent DB shortly before presenting. License verification remains a
content-specific editorial decision (per-page grant from the publisher), never
something inferred from HTTP success.
