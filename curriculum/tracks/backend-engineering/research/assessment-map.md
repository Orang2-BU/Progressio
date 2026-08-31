# Assessment Map

Completion of a resource is never evidence of mastery. Each assessment evaluates an observable outcome.

| Skill | Assessment type | Objective | Expected evidence | Mastery criteria |
|---|---|---|---|---|
| program-control-flow | coding challenge | Express stated normal and invalid paths | Source code and terminal output | All stated cases produce the specified outcome; invalid input follows an explicit path. |
| functions-and-modules | practical exercise | Decompose one feature into functions and modules | Source tree and brief dependency explanation | Functions have explicit inputs/outputs; module dependencies have no cycle; behavior is preserved. |
| git-change-workflow | practical exercise | Record a focused change safely | Repository history and `git diff`/status capture | Commit contains only the stated change; learner can identify staged versus unstaged work. |
| client-server-model | quiz | Interpret a client-server exchange | Annotated request-response diagram | Correctly labels client, server, resource, request and response; explains request independence. |
| http-messages-and-semantics | debugging task | Diagnose an incorrect HTTP exchange | Corrected request/response and rationale | Method, status, headers and body align with the stated operation and outcome. |
| api-contract-design | mini project | Specify a small API before implementation | OpenAPI document and operation rationale | Contract defines operation, input, success response and client-error response; references valid HTTP semantics. |
| api-input-validation | coding challenge | Define and enforce boundary validation | Validation rules, response examples and source code | Separates syntactic from semantic rules; rejects invalid input with a documented client-error response; does not expose internals. |

