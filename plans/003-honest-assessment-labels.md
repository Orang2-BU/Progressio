# Plan 003: Make mock and draft assessment results unmistakable

> **Executor**: Check drift, make the smallest text/conditional change, verify it, then update the index. Stop if the eligibility contract would need to change.
>
> **Drift check first**: `git diff --stat 2277b83..HEAD -- front-end/src/Proof.jsx front-end/tests/proof.test.js docs/demo-test-matrix.md`. Reinspect the lines below if changed.

## Status

- Priority P0; effort S (hours); risk LOW; confidence HIGH.
- Depends on: `plans/002-end-to-end-gates.md`. Category: correctness/UX. Planned at `2277b83`, 2026-10-01.

## Why

`MockAIAdapter` scores by matching words from the rubric (`back-end/apps/ai/adapters/mock.py:83-106`). The UI already explains this in a hint, but its result heading at `front-end/src/Proof.jsx:137` still says `Lulus assessment`. A viewer can miss the hint and mistake the simulated result for reviewed skill evidence.

## Current state and conventions

- `front-end/src/Proof.jsx:52` says mock/draft is not final; lines 67-68 show assessment mode and a warning; line 82 labels the issuance button `Buat draft demo`.
- `front-end/src/Proof.jsx:136-140` renders `Result` from server values: `s.is_passed`, `s.evaluation.provider`, and `s.evaluation.review_status`. Line 147 already labels non-final credentials correctly.
- `back-end/apps/credentials/services.py:33-40` permits final issuance only for reviewed standards, reviewed non-mock evidence and HTTP proof provider. Do not relax this gate.
- React components in this file use simple local values and JSX; match that style, with no new dependency.

## Scope

- Modify `front-end/src/Proof.jsx`, `front-end/tests/proof.test.js` only if a meaningful existing pure-helper assertion applies, and the result row in `docs/demo-test-matrix.md`.
- Do not alter grading, thresholds, credential eligibility, provider settings or data model.

## Steps and verification

1. In `Result`, derive whether `provider` is `mock`/`mock-fallback` or `review_status` is not `reviewed`. For a passing result in that state, use an explicit heading such as `Lulus simulasi (belum terverifikasi)`; preserve the current factual score, feedback and provenance. For reviewed rules/OpenAI evidence, keep an ordinary assessment pass label. Verify `rg -n 'Lulus simulasi|Lulus assessment|mock-fallback' front-end/src/Proof.jsx` shows both branches and provider handling.
2. Inspect `CredentialView` and issuance button to ensure draft status remains visible on the detail and public verification screens. Change only wording that still suggests final validity. Verify `rg -n 'draft|final|is_valid' front-end/src/Proof.jsx` finds explicit distinctions.
3. Run `npm test` and `npm run build` in `front-end/`. Expected: both exit 0. If the existing tests cannot render JSX, use the Plan 002 browser matrix to verify the visible result; do not introduce a test framework just to inspect copy.
4. Rehearse a passing rules submission and passing mock submission. Expected: the mock/draft heading says simulation, while both show the server's score and provenance. Record the result in `docs/demo-test-matrix.md`.

## Test plan and done criteria

- [ ] Node tests and Next build pass.
- [ ] A mock or draft pass cannot display the unqualified `Lulus assessment` heading.
- [ ] A failed attempt remains labelled as failed and retains server feedback.
- [ ] Draft credential remains unverified on the public page.
- [ ] Only scoped files and index status are changed.

## STOP conditions

- Submission evaluation lacks `provider`/`review_status` in the live payload; report the payload shape before designing a new rule.
- The change would require new backend semantics or a final credential policy change.

## Maintenance

If a real reviewer/provider is added later, revisit this wording alongside the actual credential gate. The label follows saved submission provenance, never a client assertion.
