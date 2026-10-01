# Plan 001: Run a seeded local frontend and backend together

> **Executor**: Follow each step and verify its expected result. Stop at the conditions below rather than switching infrastructure without recording the cause. Update `plans/README.md` when done.
>
> **Drift check first**: `git diff --stat 2277b83..HEAD -- front-end/tests/backend_server.py front-end/next.config.mjs front-end/README.md back-end/requirements.txt back-end/README.md docs/demo-runbook.md`. Compare the excerpts below if any file changed.

## Status

- Priority P0; effort S (hours); implementation risk LOW; confidence HIGH.
- Depends on: none. Category: DX/runtime. Planned at `2277b83`, 2026-10-01.

## Why

On 2026-10-01 the frontend build and 29 Node tests passed, but the browser's `/api/v1/career-tracks/` proxy returned HTTP 500 because port 8000 had no backend. `python manage.py test` stopped before discovery because Celery was not installed; Docker Desktop's daemon was unavailable. The repo already has `uv`, pinned Python dependencies, and a disposable backend server; use that route first.

## Current state and conventions

- `front-end/tests/backend_server.py:14-17` sets `DB_ENGINE=sqlite`, then line 23 sets the DB to `:memory:`. With `--catalog`, lines 36-42 migrate, run `seed_demo`, and add empty/inactive fixtures. It serves on `127.0.0.1:8011` (line 44).
- `front-end/next.config.mjs:1` uses `API_PROXY_TARGET` or `http://127.0.0.1:8000`; it is read when Next starts/builds.
- `back-end/requirements.txt` contains Celery and the remaining Django dependencies. `front-end/README.md:272-282` already describes the disposable server workflow.
- `back-end/apps/common/management/commands/seed_demo.py` imports the real curriculum and creates synthetic student/recruiter accounts. Do not copy its password into new documentation or output.
- Use PowerShell commands from the repo root. `.next/`, `node_modules/`, and `db.sqlite3` are ignored by `.gitignore`.

## Scope

- Modify only `docs/demo-runbook.md` (create), `front-end/README.md`, and `back-end/README.md` to record a working local start and troubleshooting path. Runtime code is already present; change it only through a separate scoped fix if a verified defect blocks this plan.
- Do not edit credentials, curriculum, production settings, Docker volumes, or user databases. Do not expose the dev server beyond localhost.

## Steps and verification

1. Check prerequisites from the root: `uv --version`, `python --version`, `node --version`, `npm --version`. Expected: all exit 0; Python 3.12 and Node at least 20.19. If Python 3.12 is not the default, `uv` may still fetch/select it.
2. Run `uv run --python 3.12 --with-requirements back-end/requirements.txt python back-end/manage.py check`. Expected: exit 0 and no system-check issues. This resolves the missing Celery dependency without altering the system Python installation.
3. Run `npm ci` in `front-end/`, then `npm test` and `npm run build`. Expected: install/build exit 0 and all Node tests pass. The previous baseline was 29/29.
4. In terminal A at the root, start `uv run --python 3.12 --with-requirements back-end/requirements.txt python front-end/tests/backend_server.py --catalog`. Expected: `Disposable backend: http://127.0.0.1:8011`.
5. In terminal B at `front-end/`, set `$env:API_PROXY_TARGET = 'http://127.0.0.1:8011'`, then run `npm run dev`. Expected: Next reports ready on port 3000. Run `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:3000/api/v1/career-tracks/` from a third terminal. Expected: HTTP 200 with a paginated response containing Backend Engineering.
6. Write the exact start/stop sequence and expected port checks into `docs/demo-runbook.md`; link it from the two READMEs. Verify `rg -n 'demo-runbook|8011|API_PROXY_TARGET' docs/demo-runbook.md front-end/README.md back-end/README.md` finds the commands and links.

## Test plan and done criteria

- [ ] `uv ... manage.py check` exits 0.
- [ ] `npm test` and `npm run build` exit 0.
- [ ] Direct backend catalog and Next `/api/v1/career-tracks/` both return HTTP 200 while servers run.
- [ ] `git status --short` shows only the scoped documentation (plus the status update in `plans/README.md`).

## STOP conditions

- Dependency resolution needs network access that is unavailable, or `uv` cannot select Python 3.12. Report the exact failed command.
- Port 8011 or 3000 is occupied by an unrelated process. Do not terminate it without identifying the owner.
- The disposable server fails migrations/import, or the current code differs materially from the cited behavior.

## Maintenance

The database is memory-only: stopping terminal A discards every demo attempt. Plan 005 records a preparation sequence. Use a separate persistence plan if a hosted or restart-safe demo becomes necessary. Do not run `seed_demo` against a production database.
