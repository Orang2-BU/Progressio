"""Validate the JSON-compatible YAML curriculum without external dependencies."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TRACK = ROOT / "tracks" / "backend-engineering"
ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        try:
            label = path.relative_to(ROOT)
        except ValueError:
            label = path
        raise ValueError(f"{label}: {error}") from error


def schema_validate(value, schema, path):
    allowed = schema.get("type")
    if allowed:
        allowed = allowed if isinstance(allowed, list) else [allowed]
        valid = {
            "object": isinstance(value, dict),
            "array": isinstance(value, list),
            "string": isinstance(value, str),
            "boolean": isinstance(value, bool),
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


def check_grading(assessments, gradings):
    """Every assessment needs grading data, and rule-graded ones need a usable key."""
    assessment_ids = {item["id"] for item in assessments}
    graded = {item["assessment"] for item in gradings}
    if len(graded) != len(gradings):
        raise ValueError("duplicate grading assessment")
    missing = assessment_ids - graded
    if missing:
        raise ValueError(f"assessments without grading: {', '.join(sorted(missing))}")
    unknown = graded - assessment_ids
    if unknown:
        raise ValueError(f"grading for unknown assessment: {', '.join(sorted(unknown))}")

    by_id = {item["id"]: item for item in assessments}
    for grading in gradings:
        assessment = by_id[grading["assessment"]]
        label = f"grading:{grading['assessment']}"
        if assessment["passing_score"] != grading["passing_score"]:
            raise ValueError(f"{label}: passing_score disagrees with the assessment")
        if assessment["estimated_minutes"] != grading["estimated_minutes"]:
            raise ValueError(f"{label}: estimated_minutes disagrees with the assessment")
        if grading["passing_score"] > grading["max_score"]:
            raise ValueError(f"{label}: passing_score above max_score")
        if grading["mode"] == "rules":
            questions = grading.get("questions") or []
            answer_key = grading.get("answer_key") or {}
            if not questions:
                raise ValueError(f"{label}: rule-graded assessment has no questions")
            if not answer_key:
                raise ValueError(f"{label}: rule-graded assessment has no answer key")
            question_ids = [item["id"] for item in questions]
            if len(question_ids) != len(set(question_ids)):
                raise ValueError(f"{label}: duplicate question id")
            if set(question_ids) != set(answer_key):
                raise ValueError(f"{label}: answer key does not cover every question")
            for question in questions:
                values = {option["value"] for option in question["options"]}
                if len(values) != len(question["options"]):
                    raise ValueError(f"{label}: duplicate option value in {question['id']}")
                if answer_key[question["id"]] not in values:
                    raise ValueError(f"{label}: answer for {question['id']} is not an option")
        else:
            rubric = grading.get("rubric") or []
            if not rubric:
                raise ValueError(f"{label}: AI-graded assessment has no rubric")
            if sum(item["weight"] for item in rubric) != 100:
                raise ValueError(f"{label}: rubric weights must total 100")
            if grading.get("answer_key"):
                raise ValueError(f"{label}: AI-graded assessment must not carry an answer key")


def check_diagnostics(diagnostics, skill_ids):
    """Diagnostics must target a real skill and mark a real option as correct."""
    for diagnostic in diagnostics:
        label = f"diagnostic:{diagnostic['id']}"
        if diagnostic["skill"] not in skill_ids:
            raise ValueError(f"{label}: unknown skill")
        question_ids = [item["id"] for item in diagnostic["questions"]]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError(f"{label}: duplicate question id")
        for question in diagnostic["questions"]:
            values = {option["value"] for option in question["options"]}
            if len(values) != len(question["options"]):
                raise ValueError(f"{label}: duplicate option value in {question['id']}")
            if question["correct_answer"] not in values:
                raise ValueError(f"{label}: correct_answer for {question['id']} is not an option")


def check_study_steps(study_steps, skills, resource_ids):
    """A study step must point into a resource the skill actually declares."""
    by_skill = {item["id"]: item for item in skills}
    seen_ids = set()
    for plan in study_steps:
        label = f"study-step:{plan['id']}"
        skill = by_skill.get(plan["skill"])
        if skill is None:
            raise ValueError(f"{label}: unknown skill")
        for step in plan["steps"]:
            if step["id"] in seen_ids:
                raise ValueError(f"{label}: duplicate step id {step['id']}")
            seen_ids.add(step["id"])
            if step["resource"] not in resource_ids:
                raise ValueError(f"{label}: unknown resource {step['resource']}")
            if step["resource"] not in skill["resources"]:
                raise ValueError(
                    f"{label}: resource {step['resource']} is not declared by skill "
                    f"{skill['id']}"
                )


def validate(track=TRACK, schema_dir=ROOT / "schemas"):
    manifest = load(track / "curriculum.yaml")
    version = load(track / "version.yaml")
    if set(manifest) != {"id", "title", "description", "version", "schema_version", "target_learner", "difficulty", "estimated_hours", "competencies", "metadata"}:
        raise ValueError("curriculum.yaml: unexpected or missing fields")
    competencies = records(track / "competencies")
    skills = records(track / "skills")
    resources = records(track / "resources")
    assessments = records(track / "assessments")
    gradings = records(track / "grading")
    diagnostics = records(track / "diagnostics")
    study_steps = records(track / "study-steps")
    schemas = {name: load(schema_dir / f"{name}.schema.json") for name in ["curriculum", "competency", "skill", "resource", "assessment", "grading", "diagnostic", "study-step"]}
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
    for item in gradings:
        schema_validate(item, schemas["grading"], f"grading:{item.get('assessment', '?')}")
    for item in diagnostics:
        schema_validate(item, schemas["diagnostic"], f"diagnostic:{item.get('id', '?')}")
    for item in study_steps:
        schema_validate(item, schemas["study-step"], f"study-step:{item.get('id', '?')}")
    for item in competencies:
        need(item, ["id", "title", "description", "order", "estimated_hours", "learning_outcomes", "observable_behaviors", "prerequisite_competencies", "skills"], "competency")
    for item in skills:
        need(item, ["id", "title", "competency", "description", "difficulty", "estimated_minutes", "learning_outcomes", "prerequisites", "resources", "assessments"], "skill")
    for item in resources:
        need(item, ["id", "title", "provider", "type", "role", "url", "difficulty", "supported_skills", "authority_level", "verified_at", "estimated_minutes", "license", "license_url", "license_verified", "redistributable", "attribution_required", "commercial_use_allowed"], "resource")
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
        if resource["redistributable"] and not resource["commercial_use_allowed"]:
            raise ValueError(
                f"resource {resource['id']}: marked redistributable under a "
                "non-commercial licence"
            )
    for assessment in assessments:
        if assessment["skill"] not in skill_ids:
            raise ValueError(f"assessment {assessment['id']}: unknown skill")
    diagnostic_ids = unique(diagnostics, "diagnostic")
    check_grading(assessments, gradings)
    check_diagnostics(diagnostics, skill_ids)
    check_study_steps(study_steps, skills, resource_ids)
    seen = set()
    for skill_id in skill_ids:
        visit(skill_id, graph, seen, set())
    print(
        f"OK: {len(competencies)} competencies, {len(skills)} skills, "
        f"{len(resources)} resources, {len(assessments)} assessments, "
        f"{len(gradings)} grading, {len(diagnostic_ids)} diagnostics, "
        f"{len(study_steps)} study plans"
    )


if __name__ == "__main__":
    try:
        validate()
    except ValueError as error:
        print(f"INVALID: {error}", file=sys.stderr)
        sys.exit(1)
