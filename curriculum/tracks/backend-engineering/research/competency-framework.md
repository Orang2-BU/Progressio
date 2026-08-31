# Competency Framework

## programming-fundamentals — Programming Fundamentals

**Purpose:** establish the program construction habits needed to express backend behavior without tying the curriculum to a framework.

**Description:** control flow, functions, modules, and version-control workflow for small maintainable programs.

**Observable professional behaviors:** breaks a requirement into inputs, decisions and outputs; names and extracts functions with one responsibility; keeps related behavior in modules; creates focused, reviewable commits.

**Final learning outcomes:**

- Construct a program path that handles normal and invalid inputs explicitly.
- Implement and call functions with suitable parameters and return values.
- Separate a small feature into cohesive modules with clear dependencies.
- Produce a Git history that identifies each intentional change.

**Estimated learning hours:** 18

**Prerequisite competencies:** none.

## backend-web-foundations — Backend and Web Foundations

**Purpose:** establish the client-server and HTTP model that gives backend behavior its external meaning.

**Description:** the request-response model, resource-oriented HTTP interaction, message structure, methods, headers and status codes.

**Observable professional behaviors:** traces a request from client to server and back; inspects an HTTP message; distinguishes method intent from URI naming; selects response status and headers that communicate the outcome.

**Final learning outcomes:**

- Describe the roles of client, server, request, response and resource in a web interaction.
- Construct and interpret HTTP requests and responses, including start line, headers and body.
- Select an HTTP method and status code consistent with the requested operation and outcome.

**Estimated learning hours:** 16

**Prerequisite competencies:** programming-fundamentals is recommended but not required; the client-server model may begin in parallel.

## api-development — API Development

**Purpose:** turn product behavior into a stable, consumable HTTP API boundary.

**Description:** resource and operation design, machine-readable API contracts, request validation and predictable error responses.

**Observable professional behaviors:** maps a use case to an API operation; documents inputs and outputs before implementation; rejects malformed or semantically invalid input at the boundary; explains an error response to an API consumer.

**Final learning outcomes:**

- Draft an API contract that defines operations, parameters, request bodies, responses and errors.
- Select appropriate HTTP methods and status codes for a defined API operation.
- Implement input validation rules for an API endpoint and return a consistent client-error response.

**Estimated learning hours:** 20

**Prerequisite competencies:** programming-fundamentals and backend-web-foundations.

