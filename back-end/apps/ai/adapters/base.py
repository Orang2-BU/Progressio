from abc import ABC, abstractmethod


class BaseAIAdapter(ABC):
    """
    Abstract interface for AI Services.
    Enforces Clean Architecture: Views/Services call this interface,
    never specific vendor APIs directly.
    """

    @abstractmethod
    def analyze_skill_gap(self, user_profile, target_career_track, user_skills, required_skills):
        """
        Analyzes missing competencies and recommended learning sequence.
        """
        pass

    @abstractmethod
    def generate_learning_recommendations(self, user_profile, current_progress, weak_areas):
        """
        Generates personalized next-step learning recommendations.
        """
        pass

    @abstractmethod
    def evaluate_submission(self, assessment, submission_content):
        """
        Evaluates student assessment submission and generates constructive feedback.
        """
        pass
