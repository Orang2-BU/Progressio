# Curriculum import specification

The curriculum package is the source of truth. Import is an atomic operation:

```text
YAML -> Loader -> Validator -> Seeder -> Database
```

## Validation rules

- Load only files below the selected track package; reject unknown file types.
- Validate each document against its entity schema and reject malformed YAML.
- IDs are unique within an entity type and use lowercase `a-z`, digits, `_` or `-`.
- Every competency, skill, resource, assessment and credential reference must resolve.
- Skill prerequisites form an acyclic graph and point only to skills in the track.
- Scores are 0–100; estimated times and hours are positive.
- URLs must be absolute; resource content is never imported.
- Track version must be valid semantic version and greater than the installed version for an upgrade.

## Duplicate handling

Import runs in a staging transaction. Existing records are matched by `(track_id, entity_type, id)`. Same ID and same version is a no-op; same ID with changed content requires a higher package version. IDs are never silently overwritten.

## Version migration

The importer records package version and a content checksum. Schema migrations are explicit and ordered. A package declares its minimum importer schema version; incompatible packages are rejected before seeding.

## Rollback

Validation occurs before writes. Seeding uses one database transaction; any failure rolls back all entities. The previous package version remains active until the new transaction commits. Restore is performed by re-importing the last known-good immutable package.

## Operational result

The importer reports package version, counts by entity, checksum, warnings and errors. It must not partially activate a package.

