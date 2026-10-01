# Progressio demo improvement plans

Planned against commit `2277b83` on 2026-10-01. These five tasks turn the existing Next.js and Django MVP into a repeatable **local demo**. Read the relevant plan completely before executing it. Keep the curriculum and credential labelled `draft`; these plans do not authorize final credential issuance.

## Ringkasan tugas untuk eksekusi

- [ ] 001 — Hidupkan Django seeded dan Next.js pada localhost; pastikan API lewat proxy mengembalikan 200.
- [ ] 002 — Jalankan tes kurikulum, backend, frontend, API probe, dan satu perjalanan browser beserta kasus gagal.
- [ ] 003 — Perjelas label kelulusan simulasi pada hasil assessment mock/draft.
- [ ] 004 — Perbaiki salah klasifikasi tautan HEAD 403/405, cek 13 sumber, dan catat bukti lisensi tanpa mengubah klaim yang belum pasti.
- [ ] 005 — Siapkan evidence sintetis untuk competency dua skill, latihan ulang demo, dan perbarui panduan yang usang.

## Execution order and status

| Plan | Outcome | Priority | Effort | Depends on | Status |
| --- | --- | --- | --- | --- | --- |
| [001](001-local-runtime.md) | Frontend and seeded backend run together locally | P0 | S | — | TODO |
| [002](002-end-to-end-gates.md) | Tests and a repeatable end-to-end checklist pass | P0 | M | 001 | TODO |
| [003](003-honest-assessment-labels.md) | Mock/draft results are unmistakable in the UI | P0 | S | 002 | TODO |
| [004](004-source-links-and-licenses.md) | Demo source links are checked and license claims recorded accurately | P1 | M | 001 | TODO |
| [005](005-demo-data-and-runbook.md) | Synthetic demo data and operator runbook are rehearsed | P0 | M | 002, 003, 004 | TODO |

Status values: TODO, IN PROGRESS, DONE, BLOCKED (include reason), REJECTED (include reason). Update the row only after the plan's done criteria pass. Do not publish, deploy, push, or issue a final credential as part of these plans.

## Dependency notes

- 001 establishes a working local frontend/backend pair; 002 and 004 require it.
- 002 identifies the actual UI and API behavior before 003 changes wording.
- 005 is the final rehearsal and requires the other demo gates.
- 004 can run alongside 002 and 003 after 001.

## Overall demo gate

From a fresh local start: sign in with a synthetic account; select the Backend Engineering track; complete diagnostic; view a roadmap; open a publisher-hosted lesson; submit one rules assessment and one mock assessment for Backend and Web Foundations; issue a **draft** for that competency; open its public verification URL and confirm it says invalid/unverified. The two-skill competency is declared in `curriculum/tracks/backend-engineering/competencies/backend-web-foundations.yaml`. The runtime and tests must pass, and every publisher link clicked during the demo must open in the operator's browser.

## Deliberate deferrals

- Docker/PostgreSQL/Redis deployment: the existing `front-end/tests/backend_server.py --catalog` provides a disposable local Django+SQLite server for a hackathon demo. Revisit persistence and deployment when a hosted demo is required.
- Crawler or copied lessons: `curriculum/README.md` defines URL pointers as the source package. Link out to publishers; audit reuse rights before copying content.
- Real AI, blockchain proof, and final credential: the curriculum, grading and diagnostics remain draft. Their review and provider reconciliation are separate production work.
- Mobile UI: the Next.js web flow is the demo target in `front-end/README.md`.

## Findings considered and rejected for this demo

- Replacing the mock grader now: high effort and still insufficient to claim reviewed competence; clear simulation labels are the proportionate fix.
- Building a new end-to-end test framework: existing Node, Django, curriculum, and API-probe checks cover the current flow. A short operator rehearsal catches presentation failures.
