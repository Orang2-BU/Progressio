"""
Projects a validated curriculum package onto the Django domain models.

The curriculum package is the source of truth; the database is a projection of
it. Importing is idempotent: running it twice produces the same rows. Records
created here are flagged ``is_managed`` so hand-authored content is never
touched.

Grading data lives in the package's ``grading/`` directory rather than in the
reviewed research files, because answer keys and rubrics are operational data.
Anything still marked ``review_status: draft`` is imported but reported, so an
unreviewed answer key is never mistaken for an approved one.
"""
from collections import defaultdict
from datetime import date

from django.db import transaction

from apps.assessments.models import Assessment, DiagnosticQuestion, Submission
from apps.careers.models import CareerTrack
from apps.competencies.models import Competency, CompetencyPrerequisite
from apps.learning.models import Lesson, LessonCompletion, StudyStep
from apps.skills.models import Skill, SkillPrerequisite

from . import mapping
from .loader import CurriculumError, load_package


class _Rollback(Exception):
    """Internal signal used to abort the transaction after a dry run."""


class ImportReport:
    """Counts of what an import did, or would do in a dry run."""

    def __init__(self, track_id, dry_run=False):
        self.track_id = track_id
        self.dry_run = dry_run
        self.created = defaultdict(int)
        self.updated = defaultdict(int)
        self.pruned = defaultdict(int)
        self.skipped = []
        self.warnings = []

    def record(self, kind, created):
        (self.created if created else self.updated)[kind] += 1

    @property
    def is_empty(self):
        return not (self.created or self.updated or self.pruned)

    def lines(self):
        out = []
        for kind in sorted(set(self.created) | set(self.updated) | set(self.pruned)):
            out.append(
                f'  {kind:24} created={self.created[kind]:<4} '
                f'updated={self.updated[kind]:<4} pruned={self.pruned[kind]}'
            )
        return out


class CurriculumImporter:
    """Imports one curriculum package into the database."""

    def __init__(self, track_id, dry_run=False, prune=False):
        self.track_id = track_id
        self.dry_run = dry_run
        self.prune = prune
        self.report = ImportReport(track_id, dry_run)

    def run(self):
        package = load_package(self.track_id)
        try:
            with transaction.atomic():
                self._import(package)
                if self.dry_run:
                    raise _Rollback
        except _Rollback:
            pass
        return self.report

    # --- import steps, in foreign-key order ---------------------------------

    def _import(self, package):
        manifest = package['manifest']
        version = package['version']

        track = self._import_track(manifest, version)
        competencies = self._import_competencies(track, package['competencies'])
        self._import_competency_prerequisites(package['competencies'], competencies)
        skills = self._import_skills(competencies, package['skills'])
        self._import_skill_prerequisites(package['skills'], skills)
        self._import_resources(package['resources'], skills)
        self._import_assessments(package['assessments'], package['grading'], skills)
        self._import_diagnostics(track, package['diagnostics'], skills)
        self._import_study_steps(package['study_steps'], skills)

        self._warn_about_draft_grading(
            package['grading'], package['diagnostics'], package['study_steps']
        )
        self._warn_about_unverified_licences(package['resources'])
        self._warn_about_unmanaged(track)

        if self.prune:
            self._prune(track, competencies, skills, package['resources'])

    def _import_track(self, manifest, version):
        track, created = CareerTrack.objects.update_or_create(
            slug=manifest['id'],
            defaults={
                'title': manifest['title'],
                'description': manifest['description'],
                'target_learner': manifest['target_learner'],
                'difficulty': mapping.difficulty(manifest['difficulty'], mapping.TRACK_DIFFICULTY),
                'estimated_hours': manifest['estimated_hours'],
                'curriculum_version': manifest['version'],
                'curriculum_schema_version': version['schema_version'],
                'metadata': manifest.get('metadata', {}),
                'is_active': True,
                'is_managed': True,
            },
        )
        self.report.record('career_track', created)
        return track

    def _import_competencies(self, track, records):
        competencies = {}
        for record in records:
            competency, created = Competency.objects.update_or_create(
                slug=record['id'],
                defaults={
                    'career_track': track,
                    'title': record['title'],
                    'description': record['description'],
                    'order': record['order'],
                    'estimated_hours': record['estimated_hours'],
                    'learning_outcomes': record['learning_outcomes'],
                    'observable_behaviors': record['observable_behaviors'],
                    'is_managed': True,
                },
            )
            self.report.record('competency', created)
            competencies[record['id']] = competency
        return competencies

    def _import_competency_prerequisites(self, records, competencies):
        for record in records:
            wanted = set(record['prerequisite_competencies'])
            for required_id in wanted:
                _, created = CompetencyPrerequisite.objects.get_or_create(
                    competency=competencies[record['id']],
                    required_competency=competencies[required_id],
                )
                if created:
                    self.report.record('competency_prerequisite', True)

            stale = CompetencyPrerequisite.objects.filter(
                competency=competencies[record['id']]
            ).exclude(required_competency__slug__in=wanted)
            removed = stale.count()
            if removed:
                stale.delete()
                self.report.pruned['competency_prerequisite'] += removed

    def _import_skills(self, competencies, records):
        skills = {}
        for record in records:
            competency = competencies[record['competency']]
            skill, created = Skill.objects.update_or_create(
                slug=record['id'],
                defaults={
                    'competency': competency,
                    'title': record['title'],
                    'description': record['description'],
                    'difficulty': mapping.difficulty(record['difficulty']),
                    'estimated_learning_minutes': record['estimated_minutes'],
                    'learning_outcomes': record['learning_outcomes'],
                    'is_managed': True,
                },
            )
            self.report.record('skill', created)
            skills[record['id']] = skill
        return skills

    def _import_skill_prerequisites(self, records, skills):
        for record in records:
            wanted = set(record['prerequisites'])
            for required_id in wanted:
                _, created = SkillPrerequisite.objects.get_or_create(
                    skill=skills[record['id']],
                    required_skill=skills[required_id],
                )
                if created:
                    self.report.record('skill_prerequisite', True)

            stale = SkillPrerequisite.objects.filter(
                skill=skills[record['id']]
            ).exclude(required_skill__slug__in=wanted)
            removed = stale.count()
            if removed:
                stale.delete()
                self.report.pruned['skill_prerequisite'] += removed

    def _import_resources(self, records, skills):
        """
        One curriculum resource supports one or more skills, so it becomes one
        Lesson per skill it supports. Only the pointer and its attribution are
        stored — the material itself stays at the source.
        """
        per_skill = defaultdict(list)
        for record in records:
            for skill_id in record['supported_skills']:
                per_skill[skill_id].append(record)

        for skill_id, resources in per_skill.items():
            resources.sort(key=lambda item: (mapping.role_order(item['role']), item['id']))
            for order, record in enumerate(resources):
                lesson, created = Lesson.objects.update_or_create(
                    skill=skills[skill_id],
                    source_id=record['id'],
                    is_managed=True,
                    defaults={
                        'title': record['title'],
                        'content_type': mapping.content_type(record['type']),
                        'content_url': record['url'],
                        'order': order,
                        'provider': record['provider'],
                        'authority_level': record['authority_level'],
                        'source_verified_at': date.fromisoformat(record['verified_at']),
                        # Zero until the curriculum declares one; inventing a
                        # duration would misreport effort.
                        'duration': record.get('estimated_minutes') or 0,
                        'license': record['license'],
                        'license_url': record['license_url'],
                        'license_verified': record['license_verified'],
                        'redistributable': record['redistributable'],
                        'attribution_required': record['attribution_required'],
                        'commercial_use_allowed': record['commercial_use_allowed'],
                    },
                )
                self.report.record('lesson', created)

    def _import_assessments(self, records, grading_records, skills):
        """
        Assessments carry what is assessed; the grading files carry how it is
        scored. Answer keys land in grading_config, which is never serialized,
        while the question list is public and holds no answers.
        """
        grading = {item['assessment']: item for item in grading_records}
        for record in records:
            rules = grading[record['id']]
            assessment_type, evaluation_mode = mapping.assessment_type(record['type'])
            if rules['mode'] == 'rules':
                config = {'answer_key': rules['answer_key']}
                questions = rules.get('questions', [])
            else:
                config = {'rubric': rules['rubric']}
                questions = []

            _, created = Assessment.objects.update_or_create(
                source_id=record['id'],
                is_managed=True,
                defaults={
                    'skill': skills[record['skill']],
                    'title': record['title'],
                    'assessment_type': assessment_type,
                    'evaluation_mode': evaluation_mode,
                    'instructions': record['instructions_summary'],
                    'objective': record['objective'],
                    'expected_evidence': record['expected_evidence'],
                    'mastery_criteria': record['mastery_criteria'],
                    'passing_score': rules['passing_score'],
                    'max_score': rules['max_score'],
                    'estimated_minutes': rules['estimated_minutes'],
                    'questions': questions,
                    'grading_config': config,
                },
            )
            self.report.record('assessment', created)

    def _import_diagnostics(self, track, records, skills):
        """
        Diagnostic questions are keyed by their curriculum question ID so a
        reworded prompt updates in place instead of creating a duplicate.
        """
        order = 0
        wanted = []
        for record in records:
            skill = skills[record['skill']]
            for question in record['questions']:
                order += 1
                wanted.append(question['id'])
                _, created = DiagnosticQuestion.objects.update_or_create(
                    career_track=track,
                    source_id=question['id'],
                    defaults={
                        'skill': skill,
                        'prompt': question['prompt'],
                        'options': question['options'],
                        'correct_answer': question['correct_answer'],
                        'explanation': question['explanation'],
                        'order': order,
                        'is_active': True,
                    },
                )
                self.report.record('diagnostic_question', created)

        stale = DiagnosticQuestion.objects.filter(career_track=track).exclude(
            source_id__in=wanted
        ).exclude(source_id='')
        removed = stale.count()
        if removed:
            stale.delete()
            self.report.pruned['diagnostic_question'] += removed

    def _import_study_steps(self, records, skills):
        """
        Attach authored study steps to the lesson that points at the resource
        each step covers. The checkpoint answer is stored but never serialized.
        """
        wanted = []
        for plan in records:
            skill = skills[plan['skill']]
            for order, step in enumerate(plan['steps']):
                lesson = Lesson.objects.filter(
                    skill=skill, source_id=step['resource'], is_managed=True
                ).first()
                if lesson is None:
                    raise CurriculumError(
                        f"Study step '{step['id']}' points at resource "
                        f"'{step['resource']}', which has no lesson for skill "
                        f"'{plan['skill']}'."
                    )
                wanted.append(step['id'])
                _, created = StudyStep.objects.update_or_create(
                    lesson=lesson,
                    order=order,
                    defaults={
                        'anchor': step['anchor'],
                        'prompt': step['prompt'],
                        'checkpoint_question': step['checkpoint_question'],
                        'checkpoint_answer': step['checkpoint_answer'],
                        'estimated_minutes': step['estimated_minutes'],
                    },
                )
                self.report.record('study_step', created)

    # --- deferred and safety checks ----------------------------------------

    def _warn_about_draft_grading(self, grading_records, diagnostic_records, study_records):
        draft = [
            item for item in grading_records + diagnostic_records + study_records
            if item.get('review_status') != 'reviewed'
        ]
        if draft:
            self.report.warnings.append(
                f'{len(draft)} grading, diagnostic and study files are still marked '
                'review_status: draft. Their scores and answer keys have not been '
                'through curriculum review and must not be treated as approved.'
            )

    def _warn_about_unverified_licences(self, resources):
        unverified = [item['id'] for item in resources if not item['license_verified']]
        if unverified:
            self.report.warnings.append(
                f'{len(unverified)} resource licences are declared but not yet verified '
                'against the source. Linking is unaffected; copying any of this material '
                'requires verification first.'
            )

    def _warn_about_unmanaged(self, track):
        """
        Surface hand-seeded rows that share this track, so a collision with
        seed_demo is visible rather than silent.
        """
        orphans = Competency.objects.filter(career_track=track, is_managed=False)
        if orphans.exists():
            names = ', '.join(sorted(orphans.values_list('slug', flat=True)))
            self.report.warnings.append(
                f'Track has {orphans.count()} competencies not owned by the curriculum '
                f'({names}). They were left untouched.'
            )

    def _prune(self, track, competencies, skills, resources):
        """
        Remove managed rows that the package no longer declares.

        Deleting a Skill cascades to SkillProgress and Submission, so pruning
        refuses to run while any learner data depends on the rows involved.
        """
        stale_skills = Skill.objects.filter(
            competency__career_track=track, is_managed=True
        ).exclude(slug__in=skills)
        stale_competencies = Competency.objects.filter(
            career_track=track, is_managed=True
        ).exclude(slug__in=competencies)
        resource_ids = {record['id'] for record in resources}
        stale_lessons = Lesson.objects.filter(
            skill__competency__career_track=track, is_managed=True
        ).exclude(source_id__in=resource_ids)

        blocked = []
        if Submission.objects.filter(assessment__skill__in=stale_skills).exists():
            blocked.append('submissions')
        if LessonCompletion.objects.filter(lesson__in=stale_lessons).exists():
            blocked.append('lesson completions')
        from apps.learning.models import SkillProgress

        if SkillProgress.objects.filter(skill__in=stale_skills).exists():
            blocked.append('skill progress')
        if blocked:
            raise CurriculumError(
                'Refusing to prune: learner data depends on records that would be '
                f'deleted ({", ".join(blocked)}). Retire the entries through '
                'curriculum review instead of deleting them.'
            )

        for queryset, kind in (
            (stale_lessons, 'lesson'),
            (stale_skills, 'skill'),
            (stale_competencies, 'competency'),
        ):
            count = queryset.count()
            if count:
                queryset.delete()
                self.report.pruned[kind] += count


def import_track(track_id, dry_run=False, prune=False):
    return CurriculumImporter(track_id, dry_run=dry_run, prune=prune).run()
