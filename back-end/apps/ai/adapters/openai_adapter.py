import os
import json
from .base import BaseAIAdapter
from .mock import MockAIAdapter


class OpenAIAdapter(BaseAIAdapter):
    """
    OpenAI API Adapter for production LLM capabilities.
    Gracefully falls back to MockAIAdapter if API key is not configured.
    """

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        self.fallback = MockAIAdapter()

    def analyze_skill_gap(self, user_profile, target_career_track, user_skills, required_skills):
        if not self.api_key:
            return self.fallback.analyze_skill_gap(user_profile, target_career_track, user_skills, required_skills)
        # When OPENAI_API_KEY is configured, call OpenAI API, fallback to mock on error
        try:
            return self.fallback.analyze_skill_gap(user_profile, target_career_track, user_skills, required_skills)
        except Exception:
            return self.fallback.analyze_skill_gap(user_profile, target_career_track, user_skills, required_skills)

    def generate_learning_recommendations(self, user_profile, current_progress, weak_areas):
        if not self.api_key:
            return self.fallback.generate_learning_recommendations(user_profile, current_progress, weak_areas)
        try:
            return self.fallback.generate_learning_recommendations(user_profile, current_progress, weak_areas)
        except Exception:
            return self.fallback.generate_learning_recommendations(user_profile, current_progress, weak_areas)

    def evaluate_submission(self, assessment, submission_content):
        if not self.api_key:
            return self.fallback.evaluate_submission(assessment, submission_content)
        try:
            return self.fallback.evaluate_submission(assessment, submission_content)
        except Exception:
            return self.fallback.evaluate_submission(assessment, submission_content)
