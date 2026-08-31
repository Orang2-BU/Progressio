# MVP Skill Framework

Seven skills keep the first research slice small while forming a usable path to an API boundary.

## program-control-flow

- **Competency:** programming-fundamentals
- **Description:** express program decisions, repetition and explicit failure paths from stated inputs.
- **Difficulty / time:** Beginner / 5 hours
- **Learning outcomes:** construct conditional and loop logic for a stated rule; return or raise a defined outcome for invalid input.
- **Prerequisites:** none
- **Why it matters:** backend endpoints are programs that must make correct decisions for both expected and invalid requests.

## functions-and-modules

- **Competency:** programming-fundamentals
- **Description:** separate behavior into functions and modules with clear inputs, outputs and dependencies.
- **Difficulty / time:** Beginner / 6 hours
- **Learning outcomes:** define functions with explicit arguments and return values; organize a small feature across modules without circular imports.
- **Prerequisites:** program-control-flow
- **Why it matters:** API behavior becomes difficult to change or review when all concerns are placed in one handler.

## git-change-workflow

- **Competency:** programming-fundamentals
- **Description:** use working tree, staging area and commits to create reviewable changes.
- **Difficulty / time:** Beginner / 3 hours
- **Learning outcomes:** inspect a diff before staging; create a focused commit; recover a local uncommitted mistake safely.
- **Prerequisites:** none
- **Why it matters:** backend work is collaborative and production changes must have traceable intent.

## client-server-model

- **Competency:** backend-web-foundations
- **Description:** model how a client requests a resource or operation and how a server returns a result.
- **Difficulty / time:** Beginner / 4 hours
- **Learning outcomes:** identify client, server, request, response and resource in an interaction; explain why HTTP requests are independently interpretable.
- **Prerequisites:** none
- **Why it matters:** API design choices only make sense when the boundary between caller and service is explicit.

## http-messages-and-semantics

- **Competency:** backend-web-foundations
- **Description:** construct and interpret HTTP request and response messages, methods, headers and status codes.
- **Difficulty / time:** Beginner / 8 hours
- **Learning outcomes:** interpret a request line, headers and body; select a method and status code whose semantics match an operation; construct a response that distinguishes success from client error.
- **Prerequisites:** client-server-model
- **Why it matters:** HTTP semantics are the interoperability contract between an API and every consumer.

## api-contract-design

- **Competency:** api-development
- **Description:** translate a bounded use case into documented API operations, inputs, outputs and error cases.
- **Difficulty / time:** Intermediate / 7 hours
- **Learning outcomes:** define a resource-oriented operation; document parameters, request body and responses in an OpenAPI description; identify one success and one client-error response per operation.
- **Prerequisites:** functions-and-modules, http-messages-and-semantics
- **Why it matters:** a contract lets clients, backend developers and tools agree on behavior before implementation.

## api-input-validation

- **Competency:** api-development
- **Description:** define syntactic and semantic input rules and communicate invalid requests predictably.
- **Difficulty / time:** Intermediate / 6 hours
- **Learning outcomes:** distinguish syntactic from semantic invalidity; implement validation at an API boundary; return a documented client-error response without exposing internals.
- **Prerequisites:** api-contract-design
- **Why it matters:** API boundaries receive untrusted input; early validation protects downstream behavior and makes failures usable for consumers.

