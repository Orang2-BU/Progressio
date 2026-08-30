import os
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
        if provider == 'openai' and os.getenv('OPENAI_API_KEY'):
            return OpenAIAdapter()
        return MockAIAdapter()

    @classmethod
    def perform_skill_gap_analysis(cls, user, career_track):
        """
        Gathers user skill progress and career track required skills,
        then queries AI adapter for gap analysis.
        """
        # All skills under this career track
        skills_qs = Skill.objects.filter(
            competency__career_track=career_track
        ).select_related('competency')

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

        track_data = {
            'id': career_track.id,
            'title': career_track.title,
            'description': career_track.description,
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
