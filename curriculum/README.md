# Curriculum

The measurement standard Progressio grades against. Everything the platform uses to decide *what counts as competent* lives here, and nowhere else.

This directory is the **source of truth**. The database is a projection of it, produced by `python manage.py import_curriculum` from `back-end/`. Never edit a track, competency, skill, lesson, or assessment through the Django admin — the next import will overwrite it.

## Layout

```text
curriculum/
├── validator.py     Dependency-free validator. Run by CI and by the backend importer.
├── schemas/         One JSON Schema per entity type.
├── tests/           Validation suite plus valid and invalid fixtures.
└── tracks/
    └── backend-engineering/
        ├── curriculum.yaml   Track manifest
        ├── version.yaml      Package and schema versions
        ├── research/         Approved source research the package was built from
        ├── competencies/     What a learner can do  (3)
        ├── skills/           Measurable units and their prerequisite graph  (7)
        ├── resources/        Pointers to external material, with licence  (13)
        ├── assessments/      What is assessed  (7)
        ├── grading/          How it is scored: answer keys and rubrics  (7)
        ├── diagnostics/      Placement questions  (7 files, 15 questions)
        └── study-steps/      Which section to read and what to do there  (7 files, 16 steps)
```

Files use JSON syntax because JSON is valid YAML 1.2. That lets the validator run on the standard library alone while the files stay readable by any YAML loader.

## The split that matters

`competencies/`, `skills/`, `resources/`, `assessments/` and `research/` are **reviewed research**. Changing them requires curriculum review.

`grading/`, `diagnostics/` and `study-steps/` are **operational data** — answer keys, passing scores, checkpoints. They are kept separate so a scoring tweak never looks like a change to the standard, and so answer keys are easy to locate and, later, to move out of the repository.

## Progressio references material, it does not copy it

Every `resource` is a URL plus attribution and licence. Nothing is copied from MDN, the Python documentation, OWASP, the OpenAPI specification, RFC 9110, Pro Git, or Exercism. `study-steps/` deep-links into a section and says what to do there; the material stays with its publisher, always current, with no licence burden.

The validator refuses to let a resource be marked `redistributable` under a non-commercial licence, so the Pro Git trap (CC BY-NC-SA) is caught by CI rather than by memory.

## Validate

```powershell
# from the repository root
python -m unittest discover -s curriculum -t .

# or validate the production package alone
python curriculum/validator.py
```

CI runs the same command on every change under `curriculum/`.

## Import into the backend

```powershell
cd back-end
python manage.py import_curriculum --dry-run   # report what would change
python manage.py import_curriculum             # apply
python manage.py import_curriculum --prune     # also delete entries the package dropped
```

The import validates first and writes inside one transaction, so an invalid package can never leave a half-imported database. `--prune` refuses to run when learner progress depends on the records it would delete.

## Current status

The package is `version: 0.1.0`, `status: draft`.

- Everything in `grading/`, `diagnostics/` and `study-steps/` carries `review_status: draft`. These were written to make the track runnable end to end and have **not** been through curriculum review.
- Every resource has `license_verified: false`. Licences are declared from the publishers' stated terms but not yet confirmed one by one.

The importer reports both on every run. Neither blocks linking or grading; both block copying material and publishing the track.
