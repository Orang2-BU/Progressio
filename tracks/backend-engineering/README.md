# Backend Engineering curriculum package

This track is the machine-readable conversion of the approved research in `research/`. It covers Programming Fundamentals, Backend and Web Foundations, and API Development only.

## Structure

- `curriculum.yaml` is the track manifest; `version.yaml` separates package and schema versions.
- `competencies/`, `skills/`, `resources/`, and `assessments/` hold one JSON-compatible YAML document per entity. These are the reviewed research.
- `grading/` holds how each assessment is scored: answer keys for rule-graded assessments, weighted rubrics for the rest. Kept separate from the research because it is operational data.
- `diagnostics/` holds the placement questions used to seed a learner's skill graph.
- `study-steps/` holds the authored bridge between a source and its assessment: which section to read and what to do there.
- `schemas/` at repository root defines the entity contracts.

The files use JSON syntax because JSON is valid YAML 1.2. This permits the included standard-library validator to run without a YAML dependency while remaining consumable by normal YAML loaders.

## What this package does and does not contain

It contains **pointers to material, never the material itself**. Every `resource` is a URL plus its attribution and licence. Nothing is copied from MDN, the Python documentation, OWASP, the OpenAPI specification, RFC 9110, Pro Git, or Exercism.

Two consequences follow:

- Pro Git is CC BY-NC-SA and Exercism is a service, so both are marked `redistributable: false`. Linking to them is unaffected; copying them into Progressio is not permitted.
- Every `license_verified` is currently `false`. The licences are declared from the publishers' stated terms but have not been confirmed one by one. Confirm each against its source before any material is copied.

## Validate

Run:

```text
python -m unittest discover -s tests -v
```

The command runs the production package plus valid and invalid fixtures. GitHub Actions runs this same command for relevant pushes and pull requests, and a second workflow imports the package into the backend.

## Review required before changing

Do not change IDs, learning outcomes, prerequisites, resource URLs, assessment criteria, scores, or durations without curriculum review.

Everything under `grading/`, `diagnostics/`, and `study-steps/` currently carries `review_status: draft`. These passing scores, answer keys, and checkpoints were drafted to make the track runnable end to end; they have **not** been through curriculum review and must not be presented as approved. Set `review_status: reviewed` once they have. The importer reports every draft file on each run.

`passing_score` is 70 across the track so that the assessment bar matches `CredentialService.MINIMUM_ELIGIBILITY_SCORE`. Changing one without the other would let a credential be issued against a bar nobody agreed to.
