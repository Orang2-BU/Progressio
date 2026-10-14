# TASK-047 — Study interaction regression evidence

Snapshot: `task-047-fix-revisi-ruang-belajar-task-020-dan-lengkapi-b`, implementation commit `4c75066` (`fix: isolate Study interaction state per lesson`). This is a frontend-only change in the task worktree; it is not merged.

## Change

- `StudyInteractionBoundary` is keyed by active lesson ID, so checkpoint input, pending state, errors, feedback, and completion receipts unmount with the lesson they belong to. A late response is ignored after that lesson has been left.
- The existing global completion lock remains intentional: another lesson's completion button is disabled while a completion request is in flight, but it does not show the previous lesson's busy label or receipt.
- Checkpoint links honor the server's `broken` link status.
- Added jsdom-backed interaction tests to the existing `node:test` suite and included them in `npm test`.

## Verification

All commands ran from `front-end/` on the task worktree, with mocked fetch responses and no backend/provider runtime:

| Command | Result |
|---|---|
| `npm ci --ignore-scripts` | exit 0; 60 packages installed; 0 vulnerabilities |
| `npm test` | exit 0; 59 passed, 0 failed, 0 skipped |
| `npm run build` | exit 0; optimized Next.js build, no workspace-root warning |
| `npm audit` | exit 0; 0 vulnerabilities |
| `git diff --check` | exit 0 |
| `node --experimental-test-coverage --test tests/study-interactions.test.js tests/study-flow.test.js` | exit 0; 8 passed |

Node's V8 line coverage for task modules in that focused run:

| Module | Lines | Branches | Functions |
|---|---:|---:|---:|
| `src/Study.jsx` | 87.86% | 85.26% | 77.42% |
| `src/StudyInteractions.jsx` | 91.03% | 93.22% | 100% |
| `src/study.js` | 89.01% | 75.56% | 92.31% |

Focused tests exercise the actual Study page's lesson selector, late completion response, progress 503 → unknown status → successful retry; plus lesson-local checkpoint answer/feedback, duplicate submits, completion error/retry, unknown completion disablement, repeat receipt without reward, and broken-source behavior. Existing helper tests cover that opening Study does not mark Diagnostic or Roadmap complete.

## Remaining gates

- No browser/Sokudo E2E run: integration/runtime remains held by the TASK-046 Bimo clearance recorded in the handoff.
- LSP was not available in this session; Next's production build completed its TypeScript phase successfully.
- Independent code/QA verdicts and owner approval are still required. This note records implementation evidence; it does not mark the board card Done or authorize merge.
