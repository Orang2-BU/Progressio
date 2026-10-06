"""Concurrent progress-consistency tests for diagnostic vs lesson/assessment.

The threaded tests in this module prove row-level locking on PostgreSQL:
``SELECT ... FOR UPDATE`` on the user row serializes the per-user
read-modify-write on ``SkillProgress``. They are skipped anywhere else on
purpose -- SQLite treats ``SELECT ... FOR UPDATE`` as a no-op, so a green
threaded run there would NOT prove locking. The sequential regression tests
at the bottom run on every backend.
"""
import threading
import unittest

from django.contrib.auth import get_user_model
from django.db import connection, connections
from django.test import TestCase, TransactionTestCase
from apps.assessments.models import (
    Assessment,
    DiagnosticQuestion,
    DiagnosticAttempt,
    Submission,
)
from apps.assessments.services import (
    AssessmentEvaluationService,
    DiagnosticService,
)
from apps.careers.models import CareerTrack
from apps.competencies.models import Competency
from apps.learning.models import (
    CompetencyProgress,
    Lesson,
    LessonCompletion,
    SkillProgress,
)
from apps.learning.services import ProgressService
from apps.skills.models import Skill

User = get_user_model()

requires_postgres = unittest.skipUnless(
    connection.vendor == "postgresql",
    "Concurrent row-locking proof requires PostgreSQL: "
    "SQLite ignores SELECT ... FOR UPDATE, so it cannot prove serialization.",
)


def run_concurrently(*targets, timeout=60):
    """Start each target in its own DB connection at the same barrier.

    Every worker runs on a SEPARATE database connection (Django connections
    are thread-local; each thread opens its own) and all workers are released
    simultaneously through a Barrier -- no sleep-based staggering. Any worker
    exception is re-raised in the calling thread after joining.
    """
    barrier = threading.Barrier(len(targets) + 1)
    errors = []

    def wrap(target):
        def worker():
            connections.close_all()
            try:
                # Open this thread's connection BEFORE the barrier so the
                # staggered TCP/auth handshake cannot serialize the workers
                # before the race even starts.
                connection.ensure_connection()
                barrier.wait(timeout=timeout)
                target()
            except Exception as exc:  # noqa: BLE001 -- re-raised below
                errors.append(exc)
            finally:
                connections.close_all()

        return worker

    threads = [threading.Thread(target=wrap(target)) for target in targets]
    for thread in threads:
        thread.start()
    barrier.wait(timeout=timeout)
    for thread in threads:
        thread.join(timeout=timeout)
    for thread in threads:
        assert not thread.is_alive(), "worker thread did not finish in time"
    if errors:
        raise errors[0]


@requires_postgres
class DiagnosticProgressConcurrencyTests(TransactionTestCase):
    """Interleaving writer tests -- PostgreSQL only (see module docstring)."""

    def setUp(self):
        self.user = User.objects.create_user(username="racer")
        self.other = User.objects.create_user(username="bystander")
        self.track = CareerTrack.objects.create(title="Backend", slug="backend")
        self.comp = Competency.objects.create(
            career_track=self.track, title="Foundations", slug="foundations", order=1
        )
        self.skill = Skill.objects.create(
            competency=self.comp, title="REST API", slug="rest-api"
        )
        self.lesson1 = Lesson.objects.create(
            skill=self.skill, title="Lesson one", order=1
        )
        self.lesson2 = Lesson.objects.create(
            skill=self.skill, title="Lesson two", order=2
        )
        self.questions = [
            DiagnosticQuestion.objects.create(
                career_track=self.track,
                skill=self.skill,
                prompt="Q1",
                options=[
                    {"value": "POST", "label": "POST"},
                    {"value": "GET", "label": "GET"},
                ],
                correct_answer="POST",
                order=1,
            ),
            DiagnosticQuestion.objects.create(
                career_track=self.track,
                skill=self.skill,
                prompt="Q2",
                options=[
                    {"value": "201", "label": "201"},
                    {"value": "404", "label": "404"},
                ],
                correct_answer="201",
                order=2,
            ),
        ]
        self.assessment = Assessment.objects.create(
            skill=self.skill,
            title="REST Quiz",
            passing_score=70,
            max_score=100,
            grading_config={"answer_key": {"q1": "A", "q2": "B"}},
        )
        self.high_answers = {str(q.id): q.correct_answer for q in self.questions}
        self.low_answers = {str(q.id): "definitely-wrong" for q in self.questions}

    def _progress(self, user=None):
        return SkillProgress.objects.get(
            user=user or self.user, skill=self.skill
        )

    def _competency_score(self, user=None):
        return CompetencyProgress.objects.get(
            user=user or self.user, competency=self.comp
        ).score

    def _reset_progress(self):
        SkillProgress.objects.filter(user=self.user).delete()
        CompetencyProgress.objects.filter(user=self.user).delete()
        DiagnosticAttempt.objects.filter(user=self.user).delete()
        Submission.objects.filter(user=self.user).delete()
        LessonCompletion.objects.filter(user=self.user).delete()

    def _run_race_rounds(self, workers, check, rounds=6):
        """Run simultaneous-start race rounds, resetting state between them.

        Every round releases all workers at the same Barrier (event-driven,
        no sleeps) and joins them before checking. Resetting progress to zero
        each round recreates the vulnerable read-modify-write state, so an
        unlocked writer loses the race with high probability per round while
        a correctly serialized writer passes every round deterministically.
        """
        for _ in range(rounds):
            self._reset_progress()
            run_concurrently(*workers)
            check()

    def test_concurrent_high_and_low_diagnostics_keep_highest_mastery(self):
        def check():
            progress = self._progress()
            self.assertEqual(progress.mastery, 100.0)
            self.assertEqual(progress.confidence, 1.0)
            # Diagnostics never award XP, however they interleave.
            self.assertEqual(progress.xp, 0)
            # Competency aggregate matches the final progress, not a stale read.
            self.assertEqual(self._competency_score(), 100.0)

        self._run_race_rounds(
            [
                lambda: DiagnosticService.submit(
                    self.user, self.track, self.high_answers
                ),
                lambda: DiagnosticService.submit(
                    self.user, self.track, self.low_answers
                ),
                lambda: DiagnosticService.submit(
                    self.user, self.track, self.low_answers
                ),
            ],
            check,
        )
        # Every writer's attempt is kept as history (resets clear earlier
        # rounds, so the final round's three attempts remain).
        self.assertEqual(
            DiagnosticAttempt.objects.filter(user=self.user).count(), 3
        )

    def test_concurrent_low_diagnostic_and_passing_assessment(self):
        passing = {"answers": {"q1": "A", "q2": "B"}}

        def check():
            progress = self._progress()
            # A stale diagnostic read must not drag mastery down to 0.
            self.assertEqual(progress.mastery, 100.0)
            # Assessment XP is neither lost nor doubled.
            self.assertEqual(progress.xp, ProgressService.XP_PER_ASSESSMENT)
            self.assertEqual(self._competency_score(), 100.0)

        self._run_race_rounds(
            [
                lambda: DiagnosticService.submit(
                    self.user, self.track, self.low_answers
                ),
                lambda: AssessmentEvaluationService.submit_and_evaluate(
                    self.user, self.assessment, dict(passing)
                ),
                lambda: DiagnosticService.submit(
                    self.user, self.track, self.low_answers
                ),
            ],
            check,
        )

    def test_concurrent_high_diagnostic_and_lesson_completion(self):
        def check():
            progress = self._progress()
            self.assertEqual(progress.mastery, 100.0)
            self.assertEqual(progress.xp, ProgressService.XP_PER_LESSON)
            self.assertEqual(
                LessonCompletion.objects.filter(user=self.user).count(), 1
            )
            self.assertEqual(self._competency_score(), 100.0)

        self._run_race_rounds(
            [
                lambda: DiagnosticService.submit(
                    self.user, self.track, self.high_answers
                ),
                lambda: ProgressService.complete_lesson(self.user, self.lesson1),
            ],
            check,
        )

    def test_concurrent_diagnostics_keep_users_isolated(self):
        other_answers = {str(q.id): q.correct_answer for q in self.questions}
        run_concurrently(
            lambda: DiagnosticService.submit(self.user, self.track, self.high_answers),
            lambda: DiagnosticService.submit(self.other, self.track, other_answers),
        )

        self.assertEqual(self._progress(self.user).mastery, 100.0)
        self.assertEqual(self._progress(self.other).mastery, 100.0)
        self.assertEqual(self._progress(self.user).xp, 0)
        self.assertEqual(self._progress(self.other).xp, 0)


class DiagnosticProgressRegressionTests(TestCase):
    """Backend-agnostic invariants: run on SQLite and PostgreSQL."""

    def setUp(self):
        self.user = User.objects.create_user(username="steady")
        self.track = CareerTrack.objects.create(title="Backend", slug="backend")
        self.comp = Competency.objects.create(
            career_track=self.track, title="Foundations", slug="foundations", order=1
        )
        self.skill = Skill.objects.create(
            competency=self.comp, title="REST API", slug="rest-api"
        )
        self.questions = [
            DiagnosticQuestion.objects.create(
                career_track=self.track,
                skill=self.skill,
                prompt="Q1",
                options=[{"value": "A", "label": "A"}],
                correct_answer="A",
                order=1,
            ),
            DiagnosticQuestion.objects.create(
                career_track=self.track,
                skill=self.skill,
                prompt="Q2",
                options=[{"value": "B", "label": "B"}],
                correct_answer="B",
                order=2,
            ),
        ]

    def _answers(self, correct):
        if correct:
            return {str(q.id): q.correct_answer for q in self.questions}
        return {str(q.id): "wrong" for q in self.questions}

    def test_repeat_diagnostic_never_regresses_mastery_or_awards_xp(self):
        DiagnosticService.submit(self.user, self.track, self._answers(True))
        DiagnosticService.submit(self.user, self.track, self._answers(False))

        progress = SkillProgress.objects.get(user=self.user, skill=self.skill)
        self.assertEqual(progress.mastery, 100.0)
        self.assertEqual(progress.xp, 0)
        self.assertEqual(
            DiagnosticAttempt.objects.filter(user=self.user).count(), 2
        )
        comp_progress = CompetencyProgress.objects.get(
            user=self.user, competency=self.comp
        )
        self.assertEqual(comp_progress.score, 100.0)

    def test_diagnostic_progress_is_per_user(self):
        other = User.objects.create_user(username="separate")
        DiagnosticService.submit(self.user, self.track, self._answers(True))

        self.assertEqual(
            SkillProgress.objects.get(user=self.user, skill=self.skill).mastery,
            100.0,
        )
        self.assertFalse(
            SkillProgress.objects.filter(user=other, skill=self.skill).exists()
        )
