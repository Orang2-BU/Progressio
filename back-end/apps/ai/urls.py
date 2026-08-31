from django.urls import path
from .views import SkillGapAnalysisView, LearningRecommendationsView

urlpatterns = [
    path('skill-gap-analysis', SkillGapAnalysisView.as_view(), name='ai-skill-gap-analysis'),
    path('recommendations', LearningRecommendationsView.as_view(), name='ai-recommendations'),
]
