# Backend Engineering curriculum package

This track is the machine-readable conversion of the approved research in `research/`. It covers Programming Fundamentals, Backend and Web Foundations, and API Development only.

## Structure

- `curriculum.yaml` is the track manifest; `version.yaml` separates package and schema versions.
- `competencies/`, `skills/`, `resources/`, and `assessments/` hold one JSON-compatible YAML document per entity.
- `schemas/` at repository root defines the entity contracts.

The files use JSON syntax because JSON is valid YAML 1.2. This permits the included standard-library validator to run without a YAML dependency while remaining consumable by normal YAML loaders.

## Validate

Run:

```text
python -m unittest discover -s tests -v
```

The command runs the production package plus valid and invalid fixtures. GitHub Actions runs this same command for relevant pushes and pull requests.

Future backend systems should import only validated entities and resolve IDs rather than infer behavior from filenames.

## Review required before changing

Do not change IDs, learning outcomes, prerequisites, resource URLs, assessment criteria, scores, or durations without curriculum review. `passing_score` and assessment `estimated_minutes` are `null` because approved research did not define them; they must be set before the track is published.
