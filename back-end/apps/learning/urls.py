from django.urls import path
from .views import (
    LessonListView,
    LessonDetailView,
    LessonCompleteView,
    UserProgressView,
    LearningPathView,
    RoadmapView,
    SkillStudyPlanView,
    StudyCheckpointView,
)

urlpatterns = [
    # Lessons
    path('lessons', LessonListView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>', LessonDetailView.as_view(), name='lesson-detail'),
    path('lesson/<int:pk>/complete', LessonCompleteView.as_view(), name='lesson-complete'),

    # Progress & Learning Path
    path('progress', UserProgressView.as_view(), name='user-progress'),
    path('learning-path', LearningPathView.as_view(), name='learning-path'),
    path('roadmap', RoadmapView.as_view(), name='roadmap'),

    # Study plan
    path('skills/<slug:slug>/study-plan', SkillStudyPlanView.as_view(), name='skill-study-plan'),
    path('study-steps/<int:pk>/checkpoint', StudyCheckpointView.as_view(), name='study-checkpoint'),
]
