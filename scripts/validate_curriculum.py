"""Validate the JSON-compatible YAML curriculum without external dependencies."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACK = ROOT / "tracks" / "backend-engineering" / "curriculum"
ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{path.relative_to(ROOT)}: {error}") from error


def schema_validate(value, schema, path):
    allowed = schema.get("type")
    if allowed:
        allowed = allowed if isinstance(allowed, list) else [allowed]
        valid = {
            "object": isinstance(value, dict),
            "array": isinstance(value, list),
            "string": isinstance(value, str),
            "integer": isinstance(value, int) and not isinstance(value, bool),
            "number": isinstance(value, (int, float)) and not isinstance(value, bool),
            "null": value is None,
        }
        if not any(valid.get(kind, False) for kind in allowed):
            raise ValueError(f"{path}: expected {' or '.join(allowed)}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{path}: invalid value")
    if isinstance(value, dict):
        missing = set(schema.get("required", [])) - set(value)
        if missing:
            raise ValueError(f"{path}: missing {', '.join(sorted(missing))}")
        if schema.get("additionalProperties") is False:
            unknown = set(value) - set(schema.get("properties", {}))
            if unknown:
                raise ValueError(f"{path}: unknown {', '.join(sorted(unknown))}")
        for key, child in schema.get("properties", {}).items():
            if key in value:
                schema_validate(value[key], child, f"{path}.{key}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            raise ValueError(f"{path}: too few items")
        for index, item in enumerate(value):
            schema_validate(item, schema.get("items", {}), f"{path}[{index}]")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise ValueError(f"{path}: empty string")
        if "pattern" in schema and not re.fullmatch(schema["pattern"], value):
            raise ValueError(f"{path}: invalid format")
        if schema.get("format") == "uri" and not value.startswith("https://"):
            raise ValueError(f"{path}: URL must use HTTPS")
        if schema.get("format") == "date" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError(f"{path}: invalid date")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            raise ValueError(f"{path}: below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            raise ValueError(f"{path}: above maximum")
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            raise ValueError(f"{path}: below exclusive minimum")


def records(folder):
    return [load(path) for path in sorted(folder.glob("*.yaml"))]


def need(data, keys, path):
    missing = [key for key in keys if key not in data]
    if missing:
        raise ValueError(f"{path}: missing {', '.join(missing)}")
    if not ID.fullmatch(data["id"]):
        raise ValueError(f"{path}: invalid id {data['id']}")


def unique(items, kind):
    ids = [item["id"] for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate {kind} id")
    return set(ids)


def visit(node, graph, seen, active):
    if node in active:
        raise ValueError(f"prerequisite cycle at {node}")
    if node in seen:
        return
    active.add(node)
    for parent in graph[node]:
        visit(parent, graph, seen, active)
    active.remove(node)
    seen.add(node)


def main():
    manifest = load(TRACK / "curriculum.yaml")
    version = load(TRACK / "version.yaml")
    if set(manifest) != {"id", "title", "description", "version", "schema_version", "target_learner", "difficulty", "estimated_hours", "competencies", "metadata"}:
        raise ValueError("curriculum.yaml: unexpected or missing fields")
    competencies = records(TRACK / "competencies")
    skills = records(TRACK / "skills")
    resources = records(TRACK / "resources")
    assessments = records(TRACK / "assessments")
    schemas = {name: load(ROOT / "schemas" / f"{name}.schema.json") for name in ["curriculum", "competency", "skill", "resource", "assessment"]}
    schema_validate(manifest, schemas["curriculum"], "curriculum.yaml")
    if set(version) != {"schema_version", "curriculum_version", "status"} or version["schema_version"] != manifest["schema_version"] or version["curriculum_version"] != manifest["version"]:
        raise ValueError("version.yaml: incompatible manifest version")
    for item in competencies:
        schema_validate(item, schemas["competency"], f"competency:{item.get('id', '?')}")
    for item in skills:
        schema_validate(item, schemas["skill"], f"skill:{item.get('id', '?')}")
    for item in resources:
        schema_validate(item, schemas["resource"], f"resource:{item.get('id', '?')}")
    for item in assessments:
        schema_validate(item, schemas["assessment"], f"assessment:{item.get('id', '?')}")
    for item in competencies:
        need(item, ["id", "title", "description", "order", "estimated_hours", "learning_outcomes", "observable_behaviors", "prerequisite_competencies", "skills"], "competency")
    for item in skills:
        need(item, ["id", "title", "competency", "description", "difficulty", "estimated_minutes", "learning_outcomes", "prerequisites", "resources", "assessments"], "skill")
    for item in resources:
        need(item, ["id", "title", "provider", "type", "role", "url", "difficulty", "supported_skills", "authority_level", "verified_at"], "resource")
    for item in assessments:
        need(item, ["id", "title", "skill", "type", "objective", "instructions_summary", "expected_evidence", "mastery_criteria", "passing_score", "estimated_minutes"], "assessment")
    competency_ids, skill_ids = unique(competencies, "competency"), unique(skills, "skill")
    resource_ids, assessment_ids = unique(resources, "resource"), unique(assessments, "assessment")
    if set(manifest["competencies"]) != competency_ids:
        raise ValueError("manifest competency IDs do not match competency files")
    graph = {}
    for skill in skills:
        if skill["competency"] not in competency_ids or not set(skill["resources"]) <= resource_ids or not set(skill["assessments"]) <= assessment_ids:
            raise ValueError(f"skill {skill['id']}: broken reference")
        graph[skill["id"]] = skill["prerequisites"]
    for prereqs in graph.values():
        if not set(prereqs) <= skill_ids:
            raise ValueError("unknown prerequisite")
    for competency in competencies:
        if not set(competency["skills"]) <= skill_ids or not set(competency["prerequisite_competencies"]) <= competency_ids:
            raise ValueError(f"competency {competency['id']}: broken reference")
    for resource in resources:
        if not set(resource["supported_skills"]) <= skill_ids or not resource["url"].startswith("https://"):
            raise ValueError(f"resource {resource['id']}: invalid reference or URL")
    for assessment in assessments:
        if assessment["skill"] not in skill_ids:
            raise ValueError(f"assessment {assessment['id']}: unknown skill")
    seen = set()
    for skill_id in skill_ids:
        visit(skill_id, graph, seen, set())
    print(f"OK: {len(competencies)} competencies, {len(skills)} skills, {len(resources)} resources, {len(assessments)} assessments")


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        print(f"INVALID: {error}", file=sys.stderr)
        sys.exit(1)
