# Demo rehearsal test matrix

Date: 2026-10-07. Runtime: a fresh disposable backend process with
`front-end/tests/backend_server.py --catalog` and Next.js proxied to port 8011.
The seeded account and all records are synthetic. The backend database is
in-memory and resets when its process stops.

| Area | Evidence expected | Result in this worktree |
|---|---|---|
| Runtime startup | Backend ready on 8011; Next.js on 3000; catalog contains Backend Engineering | Started `front-end/tests/backend_server.py --catalog` and Next.js with `API_PROXY_TARGET=http://127.0.0.1:8011`. Backend API returned the expected seeded track, competency, two skills, and a successful synthetic login. |
| Browser flow | Login, target, diagnostic, roadmap, lesson/checkpoint/completion, both competency assessments, draft issue, logged-out public verification | `e2e_list_flows` discovered only `e2e/assessment-mock-label.yaml`. Inline validation accepts `e2e/progressio-demo.yaml` (60 steps), but file validation reports it is not found, so it cannot be passed to `e2e_run` from this E2E workspace. The registered assessment flow was run twice and failed at login: screenshot and DOM show Username empty and the browser's required-field prompt after the Username tap/input steps. No complete browser journey is proven. |
| Assessment and draft semantics | Rules quiz and mock evidence both carry simulation/draft labels; public draft stays invalid and unanchored | Source inspection confirms the existing simulation/draft wording. No browser submission or draft issuance was completed in this run, so invalid/unanchored public behavior remains unverified here. |
| Completion replay | Repeating lesson completion does not grant another reward | The proposed flow asserts the repeat-completion message, but the flow could not be executed. No browser evidence in this run. |
| Source links and licenses | Publisher links are reachable and license rights are verified | Link-check and source-rights evidence is in `docs/source-review.md`; browser opening and reuse permission are distinct. No browser click-through was performed in this run. |

The runtime and E2E findings above are separate from Node unit tests, Django
tests, and the API probe. Keep `e2e/progressio-demo.yaml` as a candidate until
the flow is visible to `e2e_list_flows`, passes file-based `e2e_validate`, and
`e2e_run` reports success. The local candidate now targets the second visible
`Username` text match (the field label) because the broad selector did not fill
the input; this selector has passed inline schema validation but still needs a
browser run. Do not count a successful tap alone as proof of login. The local
mock runtime cannot validate an external credential provider or blockchain
anchoring.
