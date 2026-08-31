import json
import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.careers.models import CareerTrack
from apps.competencies.models import Competency, CompetencyPrerequisite
from apps.learning.models import Lesson, LessonCompletion, SkillProgress
from apps.skills.models import Skill, SkillPrerequisite

from . import loader
from .importer import import_track
from .loader import CurriculumError

TRACK_ID = 'backend-engineering'

User = get_user_model()


class CurriculumFixtureMixin:
    """Builds a throwaway copy of the real curriculum package that tests can edit."""

    def make_package(self, edit=None):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name) / 'tracks'
        shutil.copytree(loader.TRACKS_ROOT / TRACK_ID, root / TRACK_ID)
        if edit:
            edit(root / TRACK_ID / 'curriculum')
        patcher = mock.patch.object(loader, 'TRACKS_ROOT', root)
        patcher.start()
        self.addCleanup(patcher.stop)
        return root

    @staticmethod
    def rewrite(path, mutate):
        data = json.loads(path.read_text(encoding='utf-8'))
        mutate(data)
        path.write_text(json.dumps(data), encoding='utf-8')

    @staticmethod
    def drop_skill(curriculum, skill_id):
        """Remove a skill and everything that references it, keeping the package valid."""
        (curriculum / 'skills' / f'{skill_id}.yaml').unlink()

        dropped_assessments = set()
        for path in (curriculum / 'assessments').glob('*.yaml'):
            data = json.loads(path.read_text(encoding='utf-8'))
            if data['skill'] == skill_id:
                dropped_assessments.add(data['id'])
                path.unlink()
        for path in (curriculum / 'grading').glob('*.yaml'):
            if json.loads(path.read_text(encoding='utf-8'))['assessment'] in dropped_assessments:
                path.unlink()

        for folder in ('diagnostics', 'study-steps'):
            for path in (curriculum / folder).glob('*.yaml'):
                if json.loads(path.read_text(encoding='utf-8'))['skill'] == skill_id:
                    path.unlink()

        dropped_resources = set()
        for path in (curriculum / 'resources').glob('*.yaml'):
            data = json.loads(path.read_text(encoding='utf-8'))
            remaining = [item for item in data['supported_skills'] if item != skill_id]
            if not remaining:
                dropped_resources.add(data['id'])
                path.unlink()
            elif remaining != data['supported_skills']:
                data['supported_skills'] = remaining
                path.write_text(json.dumps(data), encoding='utf-8')

        for path in (curriculum / 'skills').glob('*.yaml'):
            data = json.loads(path.read_text(encoding='utf-8'))
            remaining = [item for item in data['resources'] if item not in dropped_resources]
            if remaining != data['resources']:
                data['resources'] = remaining
                path.write_text(json.dumps(data), encoding='utf-8')

        for path in (curriculum / 'competencies').glob('*.yaml'):
            data = json.loads(path.read_text(encoding='utf-8'))
            if skill_id in data['skills']:
                data['skills'] = [item for item in data['skills'] if item != skill_id]
                path.write_text(json.dumps(data), encoding='utf-8')


class CurriculumImportTests(CurriculumFixtureMixin, TestCase):
    def test_imports_the_backend_engineering_package(self):
        import_track(TRACK_ID)

        track = CareerTrack.objects.get(slug=TRACK_ID)
        self.assertEqual(track.title, 'Backend Engineering')
        self.assertEqual(track.curriculum_version, '0.1.0')
        self.assertEqual(track.difficulty, CareerTrack.Difficulty.BEGINNER)
        self.assertTrue(track.is_managed)

        self.assertEqual(Competency.objects.filter(career_track=track).count(), 3)
        self.assertEqual(Skill.objects.filter(competency__career_track=track).count(), 7)

    def test_maps_curriculum_vocabulary_onto_model_enums(self):
        import_track(TRACK_ID)

        skill = Skill.objects.get(slug='api-contract-design')
        self.assertEqual(skill.difficulty, Skill.Difficulty.INTERMEDIATE)
        self.assertEqual(skill.estimated_learning_minutes, 420)
        self.assertIn(
            'Define a resource-oriented operation.',
            skill.learning_outcomes,
        )

    def test_resolves_the_skill_graph_by_slug(self):
        import_track(TRACK_ID)

        skill = Skill.objects.get(slug='api-contract-design')
        required = set(
            SkillPrerequisite.objects.filter(skill=skill).values_list(
                'required_skill__slug', flat=True
            )
        )
        self.assertEqual(required, {'functions-and-modules', 'http-messages-and-semantics'})

    def test_imports_competency_level_prerequisites(self):
        import_track(TRACK_ID)

        pairs = set(
            CompetencyPrerequisite.objects.values_list(
                'competency__slug', 'required_competency__slug'
            )
        )
        self.assertIn(('api-development', 'backend-web-foundations'), pairs)

    def test_resources_become_attributed_lessons_without_copying_material(self):
        import_track(TRACK_ID)

        lesson = Lesson.objects.get(
            skill__slug='api-contract-design', source_id='openapi-spec'
        )
        self.assertEqual(lesson.provider, 'OpenAPI Initiative')
        self.assertEqual(lesson.authority_level, 'industry-standard')
        self.assertTrue(lesson.content_url.startswith('https://'))
        self.assertTrue(lesson.is_managed)
        # Duration is not invented: the curriculum does not declare one yet.
        self.assertEqual(lesson.duration, 0)

    def test_primary_resource_is_studied_before_practice(self):
        import_track(TRACK_ID)

        orders = dict(
            Lesson.objects.filter(skill__slug='program-control-flow').values_list(
                'source_id', 'order'
            )
        )
        self.assertLess(orders['python-control-flow'], orders['exercism-python'])

    def test_import_is_idempotent(self):
        import_track(TRACK_ID)
        counts = (Skill.objects.count(), Lesson.objects.count(), SkillPrerequisite.objects.count())

        report = import_track(TRACK_ID)

        self.assertEqual(
            (Skill.objects.count(), Lesson.objects.count(), SkillPrerequisite.objects.count()),
            counts,
        )
        self.assertEqual(sum(report.created.values()), 0)

    def test_assessments_are_imported_with_server_side_grading(self):
        from apps.assessments.models import Assessment

        import_track(TRACK_ID)

        quiz = Assessment.objects.get(source_id='client-server-model-assessment')
        self.assertEqual(quiz.evaluation_mode, Assessment.EvaluationMode.RULES)
        self.assertEqual(quiz.passing_score, 70)
        self.assertIn('answer_key', quiz.grading_config)
        # The public question list carries no answers.
        self.assertTrue(quiz.questions)
        for question in quiz.questions:
            self.assertNotIn('correct_answer', question)
            self.assertNotIn('answer', question)

        project = Assessment.objects.get(source_id='api-contract-design-assessment')
        self.assertEqual(project.evaluation_mode, Assessment.EvaluationMode.AI)
        self.assertEqual(sum(item['weight'] for item in project.grading_config['rubric']), 100)
        self.assertEqual(project.questions, [])

    def test_diagnostic_questions_are_imported_for_the_track(self):
        from apps.assessments.models import DiagnosticQuestion

        import_track(TRACK_ID)

        questions = DiagnosticQuestion.objects.filter(career_track__slug=TRACK_ID)
        self.assertEqual(questions.count(), 15)
        for question in questions:
            values = {option['value'] for option in question.options}
            self.assertIn(question.correct_answer, values)

    def test_study_steps_attach_to_the_lesson_they_point_at(self):
        from apps.learning.models import StudyStep

        import_track(TRACK_ID)

        step = StudyStep.objects.get(prompt__startswith='Read the definition of idempotent')
        self.assertEqual(step.lesson.source_id, 'rfc-9110')
        self.assertEqual(step.lesson.skill.slug, 'http-messages-and-semantics')
        self.assertTrue(step.study_url.startswith('https://www.rfc-editor.org/'))
        self.assertIn('#', step.study_url)

    def test_resource_licences_are_imported_onto_lessons(self):
        import_track(TRACK_ID)

        mdn = Lesson.objects.filter(source_id='mdn-http-messages').first()
        self.assertTrue(mdn.redistributable)
        self.assertTrue(mdn.commercial_use_allowed)

        # Pro Git is CC BY-NC-SA: linkable, not copyable into a commercial product.
        pro_git = Lesson.objects.filter(source_id='pro-git-basics').first()
        self.assertFalse(pro_git.redistributable)
        self.assertFalse(pro_git.commercial_use_allowed)

    def test_unverified_licences_are_reported(self):
        report = import_track(TRACK_ID)

        self.assertTrue(any('not yet verified' in note for note in report.warnings))

    def test_draft_grading_is_reported(self):
        report = import_track(TRACK_ID)

        self.assertTrue(any('review_status: draft' in note for note in report.warnings))

    def test_dry_run_writes_nothing(self):
        report = import_track(TRACK_ID, dry_run=True)

        self.assertEqual(report.created['skill'], 7)
        self.assertEqual(CareerTrack.objects.count(), 0)
        self.assertEqual(Skill.objects.count(), 0)


class CurriculumValidationGateTests(CurriculumFixtureMixin, TestCase):
    def test_invalid_package_is_rejected_before_any_write(self):
        def break_reference(curriculum):
            self.rewrite(
                curriculum / 'skills' / 'api-contract-design.yaml',
                lambda data: data['resources'].append('does-not-exist'),
            )

        self.make_package(break_reference)

        with self.assertRaises(CurriculumError):
            import_track(TRACK_ID)
        self.assertEqual(CareerTrack.objects.count(), 0)
        self.assertEqual(Skill.objects.count(), 0)

    def test_unknown_track_is_reported_clearly(self):
        with self.assertRaisesRegex(CurriculumError, 'No curriculum package'):
            import_track('data-science')


class CurriculumPruneTests(CurriculumFixtureMixin, TestCase):
    def setUp(self):
        import_track(TRACK_ID)
        self.user = User.objects.create_user(
            username='student', email='student@example.com', password='x'
        )

    def test_prune_removes_entries_the_package_no_longer_declares(self):
        self.make_package(lambda curriculum: self.drop_skill(curriculum, 'git-change-workflow'))

        report = import_track(TRACK_ID, prune=True)

        self.assertEqual(report.pruned['skill'], 1)
        self.assertFalse(Skill.objects.filter(slug='git-change-workflow').exists())

    def test_prune_refuses_to_delete_skills_a_learner_has_progress_in(self):
        SkillProgress.objects.create(
            user=self.user, skill=Skill.objects.get(slug='git-change-workflow'), mastery=80.0
        )
        self.make_package(lambda curriculum: self.drop_skill(curriculum, 'git-change-workflow'))

        with self.assertRaisesRegex(CurriculumError, 'Refusing to prune'):
            import_track(TRACK_ID, prune=True)
        self.assertTrue(Skill.objects.filter(slug='git-change-workflow').exists())

    def test_prune_refuses_to_delete_lessons_a_learner_has_completed(self):
        LessonCompletion.objects.create(
            user=self.user, lesson=Lesson.objects.get(source_id='pro-git-basics')
        )
        self.make_package(lambda curriculum: self.drop_skill(curriculum, 'git-change-workflow'))

        with self.assertRaisesRegex(CurriculumError, 'Refusing to prune'):
            import_track(TRACK_ID, prune=True)

    def test_import_without_prune_leaves_stale_records_alone(self):
        self.make_package(lambda curriculum: self.drop_skill(curriculum, 'git-change-workflow'))

        import_track(TRACK_ID)

        self.assertTrue(Skill.objects.filter(slug='git-change-workflow').exists())


class UnmanagedRecordTests(CurriculumFixtureMixin, TestCase):
    def test_hand_seeded_competencies_are_reported_and_left_untouched(self):
        track = CareerTrack.objects.create(slug=TRACK_ID, title='Backend Engineering')
        Competency.objects.create(
            career_track=track, slug='backend-foundations', title='Backend Foundations'
        )

        report = import_track(TRACK_ID)

        self.assertTrue(any('not owned by the curriculum' in note for note in report.warnings))
        self.assertTrue(Competency.objects.filter(slug='backend-foundations').exists())
