import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts import validate_curriculum as validator


ROOT = Path(__file__).resolve().parents[1]
TRACK = ROOT / "tracks" / "backend-engineering" / "curriculum"
FIXTURES = ROOT / "tests" / "fixtures"


class CurriculumTests(unittest.TestCase):
    def validate_copy(self, fixture=TRACK, changes=()):
        temp = tempfile.TemporaryDirectory()
        target = Path(temp.name) / "curriculum"
        shutil.copytree(fixture, target)
        for source, relative in changes:
            shutil.copyfile(source, target / relative)
        self.addCleanup(temp.cleanup)
        validator.validate(target)

    def assert_invalid(self, message, changes=()):
        with self.assertRaisesRegex(ValueError, message):
            self.validate_copy(TRACK, changes)

    def test_backend_engineering_package_passes(self):
        validator.validate(TRACK)

    def test_valid_fixture_passes(self):
        validator.validate(FIXTURES / "valid")

    def test_malformed_yaml_fixture_fails_parsing(self):
        with self.assertRaisesRegex(ValueError, "Expecting ',' delimiter"):
            validator.load(FIXTURES / "invalid" / "malformed.yaml")

    def test_missing_required_field_fails_schema_validation(self):
        self.assert_invalid("missing title", [(FIXTURES / "invalid" / "missing-title-skill.yaml", "skills/program-control-flow.yaml")])

    def test_broken_resource_reference_fails(self):
        self.assert_invalid("broken reference", [(FIXTURES / "invalid" / "broken-resource-skill.yaml", "skills/program-control-flow.yaml")])

    def test_missing_prerequisite_fails(self):
        self.assert_invalid("unknown prerequisite", [(FIXTURES / "invalid" / "unknown-prerequisite-skill.yaml", "skills/program-control-flow.yaml")])

    def test_prerequisite_cycle_fails(self):
        self.assert_invalid("prerequisite cycle", [(FIXTURES / "invalid" / "cycle-api-contract-skill.yaml", "skills/api-contract-design.yaml")])

    def test_duplicate_ids_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "curriculum"
            shutil.copytree(TRACK, target)
            shutil.copyfile(target / "skills" / "program-control-flow.yaml", target / "skills" / "duplicate.yaml")
            with self.assertRaisesRegex(ValueError, "duplicate skill id"):
                validator.validate(target)

    def test_competency_skill_consistency_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "curriculum"
            shutil.copytree(TRACK, target)
            path = target / "competencies" / "programming-fundamentals.yaml"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["skills"].append("missing-skill")
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "broken reference"):
                validator.validate(target)

    def test_grading_answer_must_be_one_of_the_offered_options(self):
        self.assert_invalid("is not an option", [(FIXTURES / "invalid" / "answer-not-an-option-grading.yaml", "grading/client-server-model-assessment.yaml")])

    def test_grading_answer_key_must_cover_every_question(self):
        self.assert_invalid("does not cover every question", [(FIXTURES / "invalid" / "uncovered-question-grading.yaml", "grading/client-server-model-assessment.yaml")])

    def test_grading_scores_must_agree_with_the_assessment(self):
        self.assert_invalid("passing_score disagrees", [(FIXTURES / "invalid" / "score-mismatch-grading.yaml", "grading/client-server-model-assessment.yaml")])

    def test_rubric_weights_must_total_one_hundred(self):
        self.assert_invalid("weights must total 100", [(FIXTURES / "invalid" / "rubric-weights-grading.yaml", "grading/api-contract-design-assessment.yaml")])

    def test_every_assessment_needs_grading_data(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "curriculum"
            shutil.copytree(TRACK, target)
            (target / "grading" / "client-server-model-assessment.yaml").unlink()
            with self.assertRaisesRegex(ValueError, "assessments without grading"):
                validator.validate(target)

    def test_diagnostic_must_target_a_known_skill(self):
        self.assert_invalid("unknown skill", [(FIXTURES / "invalid" / "unknown-skill-diagnostic.yaml", "diagnostics/program-control-flow-diagnostic.yaml")])

    def test_diagnostic_answer_must_be_one_of_the_offered_options(self):
        self.assert_invalid("is not an option", [(FIXTURES / "invalid" / "wrong-answer-diagnostic.yaml", "diagnostics/program-control-flow-diagnostic.yaml")])

    def test_noncommercial_source_cannot_be_marked_redistributable(self):
        self.assert_invalid("non-commercial licence", [(FIXTURES / "invalid" / "noncommercial-redistributable-resource.yaml", "resources/pro-git-basics.yaml")])

    def test_missing_version_file_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "curriculum"
            shutil.copytree(TRACK, target)
            (target / "version.yaml").unlink()
            with self.assertRaisesRegex(ValueError, "version.yaml"):
                validator.validate(target)


if __name__ == "__main__":
    unittest.main()
