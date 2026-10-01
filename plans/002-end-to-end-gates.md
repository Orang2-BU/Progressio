# Plan 002: Verify the complete demo path and record its gate

> **Executor**: Read this file independently, run every gate, and record results. Stop on the conditions below. Update `plans/README.md` only after all done criteria pass.
>
> **Drift check first**: `git diff --stat 2277b83..HEAD -- front-end/check_api_contract.py front-end/tests/backend_server.py front-end/package.json back-end/apps/credentials/services.py docs/demo-test-matrix.md`. Compare live code with the facts below if changed.

## Status

- Priority P0; effort M (roughly one day including investigation); risk LOW; confidence HIGH.
- Depends on: `plans/001-local-runtime.md`. Category: tests. Planned at `2277b83`, 2026-10-01.

## Why

Passing unit tests did not prove the actual browser journey: in the last check the frontend pages returned 200 while the proxy API returned 500. The demo needs a single reproducible pass through catalog, diagnostic, roadmap, study, assessment and credential verification.

## Current state and conventions

- `front-end/package.json` defines `npm test` and `npm run build`; the last local results were 29/29 and a successful build.
- `python -m unittest discover -s curriculum -t .` last passed 18/18 and validated 3 competencies, 7 skills and 13 resources.
- `front-end/check_api_contract.py:13-25` uses SQLite in memory and mock providers; lines 35-42 migrate/import and verify OpenAPI. Use it as the existing API probe.
- `back-end/apps/credentials/services.py:21-40` requires a passing completed assessment for **each** skill of a competency at the current curriculum version. Draft demo and final eligibility are separate.
- `front-end/tests/backend_server.py --catalog` provides seeded demo data on localhost:8011. Follow Plan 001 to connect Next.

## Scope

- Create `docs/demo-test-matrix.md` with exact commands, outcomes, and a dated manual result table. Modify `front-end/check_api_contract.py` or existing tests only if a reproducible contract bug requires it, with a focused regression assertion. Record a separate blocker rather than making broad application changes here.
- No provider credentials, production database, crawler, or new browser-testing dependency.

## Steps and verification

1. Run `python -m unittest discover -s curriculum -t .` at the repo root. Expected: all tests pass. Record count.
2. Set `$env:DB_ENGINE = 'sqlite'`, then run `uv run --python 3.12 --with-requirements back-end/requirements.txt python back-end/manage.py test` at root. Expected: exit 0 and all discovered Django tests pass against a temporary SQLite test database; do not point this at user data.
3. Run `uv run --python 3.12 --with-requirements back-end/requirements.txt python front-end/check_api_contract.py`. Expected: exit 0; record request count and any `SCHEMA GAP` separately from failed assertions.
4. At `front-end/`, run `npm test` and `npm run build`. Expected: all tests pass; build completes.
5. With the two localhost servers from Plan 001, run one browser journey: catalog track selection; diagnostic including an explicit unknown answer; result; roadmap; study/source/checkpoint/completion; one passing rules assessment for Client-Server Model; one failing then passing mock assessment for HTTP Messages and Semantics; Backend and Web Foundations draft issuance; public `/verify/{id}` without login. Expected: draft has `is_valid=false` or equivalent unverified status, with no final proof.
6. Check failure states: incomplete diagnostic, blank evidence, backend temporarily unavailable during a read, and login/URL restoration. Record actual UI response and whether retry recovers. Expected: no fabricated pass, XP, or credential on failures. Save a dated pass/fail row for each step in `docs/demo-test-matrix.md` and link to any genuine defect.

## Test plan and done criteria

- [ ] Curriculum, Django, API probe, Node, and Next build commands all exit 0; record their actual counts.
- [ ] The manual matrix includes successful and failure/recovery rows with actual results, not just intended behavior.
- [ ] A public draft verification page visibly says the credential is not final/valid.
- [ ] `git status --short` contains only scoped changes and `plans/README.md`.

## STOP conditions

- A required test fails twice, or the full browser flow cannot reach the next stage. Record command/route, actual status and smallest reproduction before changing scope.
- Any test requires a real AI or proof provider; this demo must remain on mock providers.
- A new fix would change a response contract or touch a file outside this plan's scope; propose a separate scoped task.

## Maintenance

Rerun this matrix after changes to assessment, credential or routing behavior. Do not confuse an API probe with a browser pass; both gates are required for the demo.
