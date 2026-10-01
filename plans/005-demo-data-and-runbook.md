# Plan 005: Rehearse a synthetic demo and publish a concise operator runbook

> **Executor**: Build on Plans 001-004, rehearse from a fresh backend process, and update the index only after the final gate passes. Keep the runbook usable without this conversation.
>
> **Drift check first**: `git diff --stat 2277b83..HEAD -- docs/demo-runbook.md docs/demo-test-matrix.md back-end/README.md front-end/README.md curriculum/tracks/backend-engineering/README.md back-end/apps/common/management/commands/seed_demo.py`. Reinspect cited behavior after any drift.

## Status

- Priority P0; effort M (rehearsal plus documentation); risk LOW; confidence HIGH.
- Depends on: `plans/002-end-to-end-gates.md`, `plans/003-honest-assessment-labels.md`, `plans/004-source-links-and-licenses.md`. Category: docs/DX. Planned at `2277b83`, 2026-10-01.

## Why

A technically working demo can still fail when the in-memory backend restarts, demo progress is missing, a public verification page exposes real evidence, or an old README sends the operator down the wrong setup path. The final output is a short, repeatable rehearsal with synthetic data and accurate claims.

## Current state and conventions

- `front-end/tests/backend_server.py:35-45` migrates and seeds when run with `--catalog`; its SQLite database disappears when the process stops. `back-end/apps/common/management/commands/seed_demo.py:25-54` creates two synthetic roles only when absent; it does **not** pre-award assessments or credentials.
- `curriculum/tracks/backend-engineering/competencies/backend-web-foundations.yaml` lists exactly two skills: `client-server-model` and `http-messages-and-semantics`. Their grading files use rules and mock AI, respectively.
- `back-end/apps/credentials/services.py:21-40` requires passing current-version evidence for both skills before a draft can be issued. `front-end/src/Proof.jsx:82,144-154` labels draft issuance and public verification.
- `back-end/README.md:32` still describes four skills/eight diagnostics; the current package validator reports seven skills and 15 diagnostic questions. `curriculum/tracks/backend-engineering/README.md:34` references a nonexistent `CredentialService.MINIMUM_ELIGIBILITY_SCORE` constant. Match actual code rather than preserving those claims.
- `back-end/apps/verification/serializers.py` exposes name, score and evidence links publicly. Use synthetic names and repositories only.

## Scope

- Modify only `docs/demo-runbook.md`, `docs/demo-test-matrix.md`, `back-end/README.md`, `front-end/README.md`, and `curriculum/tracks/backend-engineering/README.md`. Update `plans/README.md` status.
- Do not add completed submissions by direct database writes, change grading thresholds, enable final issuance, or reuse personal evidence. Do not put the fixed demo password in new docs; point to `seed_demo.py` for local operators.

## Steps and verification

1. Start fresh using Plan 001. Confirm the disposable backend logs its ready address, Next serves `/catalog`, and the catalog API returns Backend Engineering. Record command and expected output in `docs/demo-runbook.md`.
2. Use the seeded student account (credentials live in `seed_demo.py`) and a separate synthetic demonstration identity if screenshots will be shared. Prepare two passing submissions **through the UI** for Backend and Web Foundations: the Client-Server Model rules quiz, then a substantive HTTP Messages and Semantics evidence example showing a faulty request/response, correction and source reasoning. Expect the competency eligibility screen to list no missing skills and offer `Buat draft demo`.
3. Issue the draft once and open its verification URL in a logged-out/private browser. Expected: `status=draft`, no confirmed proof, and an explicit not-valid/final message. Capture only non-sensitive result IDs/URLs in the runbook; never capture tokens or real personal data. Repeating issuance with identical evidence should return the same draft.
4. Rehearse the full presentation order: new learner diagnostic and roadmap; link-out to a publisher-hosted lesson; checkpoint/completion; prepared student assessment evidence; draft and public verification. Time the flow and note any external page that fails. Save a short fallback route that uses already-open tabs or another verified link, without claiming the failed source is reachable.
5. Correct stale setup/count/eligibility statements in the three READMEs named in Scope. Run `rg -n 'four skills|eight diagnostic|51 tests|MINIMUM_ELIGIBILITY_SCORE' back-end/README.md front-end/README.md curriculum/tracks/backend-engineering/README.md` → no stale **current-state** claim remains. Historical phase notes may remain if clearly dated.
6. Rerun `npm test`, `npm run build`, `python -m unittest discover -s curriculum -t .`, and the backend test command from Plan 002. Expected: all pass. Run `git status --short` and confirm only scoped docs plus the index changed in this plan.

## Test plan and done criteria

- [ ] A fresh server start and one complete rehearsal pass, with timings and results recorded in `docs/demo-test-matrix.md`.
- [ ] A synthetic two-assessment competency produces a draft; public verification without login says invalid/unverified.
- [ ] Restart behavior and the need to reprepare in-memory evidence are explicit in the runbook.
- [ ] READMEs match the current seven-skill package and evidence-based credential gate.
- [ ] All four verification commands in Step 6 pass; no real identity, token, or password appears in the new docs.

## STOP conditions

- Draft requires more than the two declared skill assessments, or the public page claims a draft is valid. Report the actual payload and route before altering issuance rules.
- A demo account contains real personal information or evidence: switch to a clean disposable backend; do not publish a screenshot of the record.
- Rehearsal requires a provider or database outside the local mock setup; report the missing dependency instead of presenting a simulation as live.

## Maintenance

Repeat the link preflight and fresh-start rehearsal on the day of the presentation. Production-grade credentialing still requires curriculum review, source-rights verification, non-mock evaluation and a confirmed proof provider.
