import os
from django.core.exceptions import ImproperlyConfigured
from .adapters.mock import MockAIAdapter
from .adapters.openai_adapter import OpenAIAdapter
from apps.careers.models import CareerTrack
from apps.skills.models import Skill
from apps.learning.models import SkillProgress


class AIService:
    """
    High-level AI Service Layer.
    Orchestrates domain data extraction and delegates to the configured AI Adapter.
    """

    @classmethod
    def get_adapter(cls):
        provider = os.getenv('AI_PROVIDER', 'mock').lower()
        if provider == 'openai':
            if not os.getenv('OPENAI_API_KEY'):
                raise ImproperlyConfigured(
                    'OPENAI_API_KEY must be set when AI_PROVIDER=openai. '
                    'Use AI_PROVIDER=mock for deterministic offline development.'
                )
            return OpenAIAdapter()
        if provider == 'mock':
            return MockAIAdapter()
        raise ImproperlyConfigured(f"Unsupported AI_PROVIDER '{provider}'.")

    @classmethod
    def perform_skill_gap_analysis(cls, user, career_track, target_skill=None, target_competency=None):
        """
        Gathers user skill progress and the skills a target requires, then
        queries the AI adapter for gap analysis.

        Without a narrower target the whole track is compared, which answers
        "how close am I to this career". Passing a target skill or competency
        narrows the comparison to that goal and everything it depends on, which
        answers "how close am I to this specific thing I picked".
        """
        skills_qs = Skill.objects.filter(
            competency__career_track=career_track
        ).select_related('competency')

        if target_skill is not None or target_competency is not None:
            from apps.learning.services import LearningPathService

            roadmap = LearningPathService.get_roadmap(
                user,
                target_skill=target_skill,
                target_competency=target_competency,
            )
            in_scope = {step['skill_id'] for step in roadmap['steps']}
            in_scope |= set(
                Skill.objects.filter(
                    slug__in=[item['skill_slug'] for item in roadmap['already_satisfied']]
                ).values_list('id', flat=True)
            )
            skills_qs = skills_qs.filter(id__in=in_scope)

        required_skills = [
            {
                'id': s.id,
                'title': s.title,
                'difficulty': s.difficulty,
                'estimated_learning_minutes': s.estimated_learning_minutes,
                'competency': s.competency.title,
            }
            for s in skills_qs
        ]

        # User's current skill progresses
        user_progresses = SkillProgress.objects.filter(
            user=user,
            skill__in=skills_qs
        ).select_related('skill')

        user_skills = [
            {
                'id': p.skill_id,
                'title': p.skill.title,
                'mastery': p.mastery,
                'xp': p.xp,
                'confidence': p.confidence,
            }
            for p in user_progresses
        ]

        user_profile = {
            'username': user.username,
            'email': user.email,
        }

        target = target_skill or target_competency or career_track
        track_data = {
            'id': career_track.id,
            'title': target.title,
            'description': getattr(target, 'description', ''),
        }

        adapter = cls.get_adapter()
        return adapter.analyze_skill_gap(user_profile, track_data, user_skills, required_skills)

    @classmethod
    def get_learning_recommendations(cls, user):
        """
        Identifies weak areas (skills in progress with mastery < 70) and requests AI recommendations.
        """
        weak_progresses = SkillProgress.objects.filter(
            user=user,
            mastery__lt=70.0,
            mastery__gt=0.0
        ).select_related('skill')

        weak_areas = [
            {
                'id': p.skill.id,
                'title': p.skill.title,
                'mastery': p.mastery,
                'confidence': p.confidence,
            }
            for p in weak_progresses
        ]

        user_profile = {
            'username': user.username,
        }

        adapter = cls.get_adapter()
        return adapter.generate_learning_recommendations(user_profile, {}, weak_areas)
