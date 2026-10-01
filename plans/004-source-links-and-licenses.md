# Plan 004: Verify source links and record publisher license evidence

> **Executor**: Fix only the confirmed link-check classification, inspect all declared sources, and keep unverified rights unverified. Run the checks below before marking this done.
>
> **Drift check first**: `git diff --stat 2277b83..HEAD -- back-end/apps/learning/tasks.py back-end/apps/learning/test_study.py curriculum/tracks/backend-engineering/resources docs/source-review.md`. Reinspect live code if any path changed.

## Status

- Priority P1; effort M (about a day); risk MED (external sites differ); confidence HIGH for code issue, MED for individual URL availability.
- Depends on: `plans/001-local-runtime.md`. Category: correctness/docs. Planned at `2277b83`, 2026-10-01.

## Why

All 13 resources in `curriculum/tracks/backend-engineering/resources/` are URL pointers with `license_verified: false`. The last external fetch opened 12 pages; Python control flow returned a transient 503 from that checker. `back-end/apps/learning/tasks.py:34-38` currently treats HEAD 403/405 as `ok` without proving GET works, so the UI can advertise a source that a learner cannot open.

## Current state and conventions

- `back-end/apps/learning/tasks.py:23-40` returns `ok`, `moved`, or `broken` from HEAD. The Celery task at lines 43-65 stores status and timestamp on managed lessons, without editing the package.
- `back-end/apps/learning/test_study.py:114-140` mocks `urllib.request.urlopen` for the existing `ok`, redirect and persisted-status tests. Extend those focused tests.
- `back-end/apps/learning/management/commands/check_links.py` exposes `python manage.py check_links` and reports non-OK records. `front-end/src/Study.jsx:103-105` displays the license verification and last link status.
- `curriculum/README.md:67-70` labels the operational package draft and every resource license unverified. `curriculum/tracks/backend-engineering/README.md:8-16` says resources link to, not copy, publisher material.

## Scope

- Modify `back-end/apps/learning/tasks.py` and `back-end/apps/learning/test_study.py`. Create `docs/source-review.md`. Update a file in `curriculum/tracks/backend-engineering/resources/` only if its exact URL or rights claim is verified against that publisher's primary source; run curriculum validation afterward.
- Do not crawl, store or republish source content. Do not set `license_verified=true` based only on a generic license page. Do not invent a fourth link state without a separate migration/UI plan.

## Steps and verification

1. Add a focused test for HEAD 403/405 followed by successful GET, and for HEAD 403/405 followed by GET 403. Expected: success is `ok`/`moved` according to the final URL; denial is `broken`. Avoid reading or storing the response body. Set `$env:DB_ENGINE = 'sqlite'`, then run `uv run --python 3.12 --with-requirements back-end/requirements.txt python back-end/manage.py test apps.learning.test_study` → exit 0.
2. Change `check_url` to attempt GET only when HEAD returned 403/405, closing the response promptly and using its final URL for `moved`. Preserve the three existing return values and timeout. Rerun the focused test → exit 0.
3. Inspect all 13 URL values from the resource package and open each in a browser or equivalent GET check. Recheck `python-control-flow` explicitly; 503 alone is inconclusive. Run `python -m unittest discover -s curriculum -t .` → exit 0. Do not alter a URL unless the publisher confirms its replacement.
4. Create `docs/source-review.md` with one row per resource ID: source URL, latest check date/result, publisher license page, whether the license was verified for that **specific content**, and any attribution/reuse restriction. Distinguish link access from content reuse. Run `rg -n 'license_verified' curriculum/tracks/backend-engineering/resources` and confirm every flag changed, if any, has a matching evidence row.
5. With a populated local demo backend, run `uv run --python 3.12 --with-requirements back-end/requirements.txt python back-end/manage.py check_links` using the same DB settings as that server. Expected: all demo-clicked links have an acceptable fresh status; investigate `moved`/`broken` lines manually. Note: the disposable in-memory server uses its own database, so a separate command process cannot inspect it. If using that server, rely on the browser checklist for live status and run `check_links` only against an explicitly created disposable persistent SQLite DB.

## Test plan and done criteria

- [ ] Focused HEAD/GET regressions and curriculum tests pass.
- [ ] Every one of the 13 resources has a dated source-review row; the demo-clicked URLs open in the operator browser.
- [ ] No unverified license is represented as safe for copying.
- [ ] `git status --short` contains only scoped files and the index update.

## STOP conditions

- A publisher blocks automated GET or rate limits requests: record `unconfirmed` in the review rather than repeatedly hammering it or claiming `ok`.
- A rights claim is ambiguous across platform, community and user-contributed content (notably Exercism): retain `license_verified=false` and report it.
- A URL change affects multiple package references or requires changing the schema: request a separate scoped plan.

## Maintenance

Link health changes over time; check shortly before presenting. License verification is a content-specific editorial decision, not something inferred from HTTP success.
