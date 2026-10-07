from collections import defaultdict
import math
import os
from django.contrib.auth import get_user_model

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.learning.models import SkillProgress
from apps.learning.services import ProgressService

from .models import DiagnosticAttempt, DiagnosticQuestion, Submission


class AssessmentEvaluationService:
    """Server-side assessment lifecycle and grading orchestration."""

    @classmethod
    @transaction.atomic
    def submit_and_evaluate(cls, user, assessment, content, request_id=None):
        # ponytail: per-user transaction lock includes synchronous grading; use jobs if latency/throughput grows.
        get_user_model().objects.select_for_update().get(pk=user.pk)
        if request_id:
            previous = Submission.objects.filter(user=user, request_id=request_id).first()
            if previous:
                if previous.assessment_id != assessment.pk or previous.content != content:
                    raise ValidationError({'request_id': 'This request ID already belongs to a different payload.'})
                return previous
        if assessment.max_score <= 0 or assessment.passing_score > assessment.max_score:
            raise ValidationError({'detail': 'Assessment scoring configuration is invalid.'})
        if assessment.evaluation_mode == 'ai' and not any(
            isinstance(content.get(key), str) and content[key].strip() for key in ('code', 'text')
        ):
            raise ValidationError({'content': 'Supply code or evidence text. URLs alone are not evaluated.'})
        if assessment.evaluation_mode == 'rules' and assessment.questions:
            answers = content.get('answers')
            if not isinstance(answers, dict) or set(answers) != {str(q['id']) for q in assessment.questions}:
                raise ValidationError({'content': 'Answer every public question, and no unknown question.'})
            for question in assessment.questions:
                if answers[str(question['id'])] not in [option['value'] for option in question['options']]:
                    raise ValidationError({'content': 'Select an available answer option.'})
        submission = Submission.objects.create(
            request_id=request_id,
            user=user,
            assessment=assessment,
            content=content,
            status=Submission.Status.SUBMITTED,
            submitted_at=timezone.now(),
        )

        submission.status = Submission.Status.EVALUATING
        submission.save(update_fields=['status'])

        if assessment.evaluation_mode == assessment.EvaluationMode.AI:
            evaluation = cls._evaluate_with_ai(assessment, content)
        else:
            evaluation = cls._evaluate_with_rules(assessment, content)

        return cls.complete_evaluation(submission.pk, evaluation)

    @classmethod
    @transaction.atomic
    def complete_evaluation(cls, submission_id, evaluation):
        """Atomically persist a validated result and its one-time reward."""
        submission_ref = Submission.objects.only('user_id').get(pk=submission_id)
        user = get_user_model().objects.select_for_update().get(pk=submission_ref.user_id)
        submission = Submission.objects.select_for_update().select_related(
            'assessment__skill__competency__career_track'
        ).get(pk=submission_id)
        if submission.status == Submission.Status.COMPLETED:
            return submission

        try:
            if not isinstance(evaluation, dict):
                raise ValueError()
            raw_score = float(evaluation['score'])
            if not math.isfinite(raw_score):
                raise ValueError()
        except (ValueError, TypeError, KeyError) as exc:
            raise ValidationError({'detail': 'Evaluator returned an invalid score; no result was saved.'}) from exc

        assessment = submission.assessment
        if assessment.max_score <= 0 or assessment.passing_score > assessment.max_score:
            raise ValidationError({'detail': 'Assessment scoring configuration is invalid.'})
        score = round(max(0.0, min(raw_score, float(assessment.max_score))), 2)
        feedback = evaluation.get('feedback') or cls._default_feedback(assessment, score)
        track = assessment.skill.competency.career_track
        provider = evaluation.get('provider') or (
            'rules' if assessment.evaluation_mode == 'rules'
            else os.getenv('AI_PROVIDER', 'mock').lower()
        )
        submission.score = score
        submission.feedback = feedback
        submission.evaluation = {
            'provider': provider,
            'review_status': assessment.grading_config.get('review_status', 'unreviewed'),
            'curriculum_version': track.curriculum_version,
            'curriculum_schema_version': track.curriculum_schema_version,
            'passing_score': assessment.passing_score,
            'max_score': assessment.max_score,
            'skill_id': assessment.skill_id,
            'objective': assessment.objective,
            'mastery_criteria': assessment.mastery_criteria,
            'expected_evidence': assessment.expected_evidence,
            'rubric': assessment.grading_config.get('rubric', []),
        }
        submission.status = Submission.Status.COMPLETED
        submission.save(update_fields=['score', 'feedback', 'status', 'evaluation'])

        if submission.is_passed:
            ProgressService.record_assessment_passed(
                user=user,
                skill=assessment.skill,
                score=score / assessment.max_score * 100,
            )
        return submission

    @staticmethod
    def _evaluate_with_rules(assessment, content):
        answer_key = assessment.grading_config.get('answer_key', {})
        if not isinstance(answer_key, dict) or not answer_key:
            raise ValidationError({
                'detail': 'This rule-based assessment has no server-side answer key configured.'
            })

        answers = content.get('answers', {})
        if not isinstance(answers, dict):
            raise ValidationError({'content.answers': 'Answers must be an object keyed by question ID.'})

        correct = sum(
            1
            for question_id, expected in answer_key.items()
            if str(answers.get(str(question_id), '')).strip().casefold()
            == str(expected).strip().casefold()
        )
        total = len(answer_key)
        score = round((correct / total) * float(assessment.max_score), 2)
        return {
            'score': score,
            'feedback': (
                f'Rule-based evaluation: {correct} of {total} answers correct '
                f'({score}/{assessment.max_score}).'
            ),
        }

    @staticmethod
    def _evaluate_with_ai(assessment, content):
        from apps.ai.services import AIService

        try:
            evaluation = AIService.get_adapter().evaluate_submission(assessment, content)
        except Exception as exc:
            raise ValidationError({'detail': 'Evaluation service unavailable; no result was saved. Retry with the same request ID.'}) from exc
        if not isinstance(evaluation, dict) or evaluation.get('score') is None:
            raise ValidationError({'detail': 'AI provider returned an invalid evaluation result.'})
        return evaluation

    @staticmethod
    def _default_feedback(assessment, score):
        if score >= assessment.passing_score:
            return f'You scored {score}/{assessment.max_score} and passed the assessment.'
        return (
            f'You scored {score}/{assessment.max_score}. Minimum passing score is '
            f'{assessment.passing_score}. Review the feedback and try again.'
        )


class DiagnosticService:
    """Grades a career diagnostic and projects the result into the skill graph."""

    MASTERY_THRESHOLD = 70.0

    @classmethod
    @transaction.atomic
    def submit(cls, user, career_track, answers):
        # Same per-user serialization as lesson/assessment writers: hold the
        # user row lock before reading SkillProgress so concurrent diagnostics
        # (or a diagnostic racing an assessment/lesson) cannot interleave a
        # read-modify-write and regress mastery with a stale lower score.
        get_user_model().objects.select_for_update().get(pk=user.pk)
        questions = list(
            DiagnosticQuestion.objects.filter(
                career_track=career_track,
                skill__competency__career_track=career_track,
                is_active=True,
            ).select_related('skill', 'skill__competency')
        )
        if not questions:
            raise ValidationError({'detail': 'No active diagnostic questions exist for this career track.'})

        normalized_answers = {str(key): value for key, value in answers.items()}
        expected_ids = {str(question.id) for question in questions}
        missing_ids = sorted(expected_ids - set(normalized_answers))
        if missing_ids:
            raise ValidationError({
                'answers': f'All diagnostic questions are required. Missing IDs: {", ".join(missing_ids)}.'
            })

        by_skill = defaultdict(lambda: {'correct': 0, 'total': 0, 'skill': None})
        for question in questions:
            selected = str(normalized_answers.get(str(question.id), '')).strip().casefold()
            expected = str(question.correct_answer).strip().casefold()
            bucket = by_skill[question.skill_id]
            bucket['skill'] = question.skill
            bucket['total'] += 1
            if selected == expected:
                bucket['correct'] += 1

        skill_scores = []
        affected_competencies = set()
        for skill_id, result in by_skill.items():
            skill = result['skill']
            score = round((result['correct'] / result['total']) * 100.0, 1)
            skill_scores.append({
                'skill_id': skill_id,
                'skill_title': skill.title,
                'score': score,
                'correct_answers': result['correct'],
                'total_questions': result['total'],
            })

            progress, _ = SkillProgress.objects.get_or_create(user=user, skill=skill)
            progress.mastery = max(progress.mastery, score)
            progress.confidence = max(progress.confidence, round(score / 100.0, 2))
            progress.last_assessed_at = timezone.now()
            progress.save(update_fields=['mastery', 'confidence', 'last_assessed_at', 'updated_at'])
            affected_competencies.add(skill.competency_id)

        skill_scores.sort(key=lambda item: (item['score'], item['skill_id']))
        weak_skill_ids = [
            item['skill_id'] for item in skill_scores if item['score'] < cls.MASTERY_THRESHOLD
        ]
        overall_score = round(
            sum(item['correct_answers'] for item in skill_scores)
            / sum(item['total_questions'] for item in skill_scores)
            * 100.0,
            1,
        )

        for competency_id in affected_competencies:
            competency = next(
                item['skill'].competency
                for item in by_skill.values()
                if item['skill'].competency_id == competency_id
            )
            ProgressService.recalculate_competency_progress(user, competency)

        return DiagnosticAttempt.objects.create(
            user=user,
            career_track=career_track,
            answers=normalized_answers,
            skill_scores=skill_scores,
            weak_skill_ids=weak_skill_ids,
            overall_score=overall_score,
            completed_at=timezone.now(),
        )
