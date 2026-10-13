import math
import os
import re
from django.core.exceptions import ImproperlyConfigured
from .adapters.mock import MockAIAdapter
from .adapters.http_adapter import AIProviderProtocolError, HttpAIAdapter
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
        provider = os.getenv('AI_PROVIDER', 'mock').strip().lower()
        if provider == 'groq':
            from .adapters.groq import GroqAIAdapter
            return GroqAIAdapter()
        if provider == 'http':
            if not os.getenv('AI_API_URL', '').strip():
                raise ImproperlyConfigured(
                    'AI_API_URL must be set when AI_PROVIDER=http. '
                    'Use AI_PROVIDER=mock for deterministic offline development.'
                )
            return HttpAIAdapter()
        if provider == 'openai':
            # Deprecated alias: dipetakan ke adapter HTTP universal.
            from .adapters.openai_adapter import OpenAIAdapter
            return OpenAIAdapter()
        if provider == 'mock':
            return MockAIAdapter()
        raise ImproperlyConfigured(f"Unsupported AI_PROVIDER '{provider}'. Expected 'mock' or 'http'.")

    @classmethod
    def evaluate_submission(cls, assessment, submission_content):
        adapter = cls.get_adapter()
        result = adapter.evaluate_submission(assessment, submission_content)
        if not isinstance(result, dict):
            return result
        if result.get('provider') == 'mock-fallback':
            result.pop('model', None)
            return result
        provider = getattr(adapter, 'provider_name', None)
        result['provider'] = provider if isinstance(provider, str) else 'unknown'
        result.pop('model', None)
        model = getattr(adapter, 'model', None)
        if isinstance(model, str) and model:
            result['model'] = model
        return result

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

        user_profile = {'username': user.username}

        target = target_skill or target_competency or career_track
        track_data = {
            'id': career_track.id,
            'title': target.title,
            'description': getattr(target, 'description', ''),
        }

        adapter = cls.get_adapter()
        result = adapter.analyze_skill_gap(user_profile, track_data, user_skills, required_skills)
        from .serializers import SkillGapAnalysisResponseSerializer
        serializer = SkillGapAnalysisResponseSerializer(data=result)
        if not serializer.is_valid():
            raise AIProviderProtocolError('AI provider returned an invalid skill-gap response.')
        data = serializer.validated_data
        required_by_id = {item['id']: item for item in required_skills}
        user_by_id = {item['id']: item for item in user_skills}
        response_skills = data['missing_skills'] + data['acquired_skills']
        response_ids = [item['id'] for item in response_skills]
        if (any(isinstance(item['id'], bool) or item['id'] not in required_by_id
                for item in response_skills)
                or len(response_ids) != len(set(response_ids))):
            raise AIProviderProtocolError('AI provider returned skill IDs outside the request.')

        missing = []
        acquired = []
        for skill in required_skills:
            progress = user_by_id.get(skill['id'], {})
            mastery = progress.get('mastery', 0)
            if isinstance(mastery, bool) or not math.isfinite(float(mastery)) or not 0 <= float(mastery) <= 100:
                raise AIProviderProtocolError('Stored skill progress is invalid.')
            if float(mastery) >= 70:
                acquired.append({key: skill[key] for key in ('id', 'title', 'difficulty')})
            else:
                missing.append({
                    'id': skill['id'], 'title': skill['title'], 'difficulty': skill['difficulty'],
                    'current_mastery': float(mastery),
                    'estimated_minutes': skill['estimated_learning_minutes'],
                })
        data['target_career_track'] = track_data['title']
        data['missing_skills'] = missing
        data['acquired_skills'] = acquired
        data['match_percentage'] = round(len(acquired) * 100 / len(required_skills), 1) if required_skills else 0
        data['recommended_priority_skill'] = missing[0]['title'] if missing else None
        return data

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
        result = adapter.generate_learning_recommendations(user_profile, {}, weak_areas)
        from .serializers import LearningRecommendationsResponseSerializer
        serializer = LearningRecommendationsResponseSerializer(data=result)
        if not serializer.is_valid():
            raise AIProviderProtocolError('AI provider returned invalid recommendations.')
        data = serializer.validated_data
        hours = data['estimated_weekly_study_hours']
        allowed_skill_ids = {item['id'] for item in weak_areas}
        if not math.isfinite(hours) or hours < 0 or hours > 80:
            raise AIProviderProtocolError('AI provider returned an invalid study-time estimate.')
        for item in data['recommendations']:
            action = item['action_url']
            if action == '/api/v1/learning-path':
                continue
            match = re.fullmatch(r'/api/v1/skills/(\d+)/lessons', action)
            if not match or int(match.group(1)) not in allowed_skill_ids:
                raise AIProviderProtocolError('AI provider returned an unknown recommendation route.')
            if any(len(item[field]) > 1000 for field in ('title', 'reason')):
                raise AIProviderProtocolError('AI provider returned oversized recommendation text.')
        data['student_name'] = user.username
        return data
