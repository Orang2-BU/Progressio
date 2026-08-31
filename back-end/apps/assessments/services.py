from collections import defaultdict

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
    def submit_and_evaluate(cls, user, assessment, content):
        submission = Submission.objects.create(
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

        score = max(0.0, min(float(evaluation['score']), float(assessment.max_score)))
        feedback = evaluation.get('feedback') or cls._default_feedback(assessment, score)

        submission.score = round(score, 2)
        submission.feedback = feedback
        submission.status = Submission.Status.COMPLETED
        submission.save(update_fields=['score', 'feedback', 'status'])

        if submission.is_passed:
            ProgressService.record_assessment_passed(
                user=user,
                skill=assessment.skill,
                score=submission.score,
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

        evaluation = AIService.get_adapter().evaluate_submission(assessment, content)
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
