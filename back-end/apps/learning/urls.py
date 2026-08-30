from django.urls import path
from .views import (
    LessonListView,
    LessonDetailView,
    LessonCompleteView,
    UserProgressView,
    LearningPathView,
)

urlpatterns = [
    # Lessons
    path('lessons', LessonListView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>', LessonDetailView.as_view(), name='lesson-detail'),
    path('lesson/<int:pk>/complete', LessonCompleteView.as_view(), name='lesson-complete'),

    # Progress & Learning Path
    path('progress', UserProgressView.as_view(), name='user-progress'),
    path('learning-path', LearningPathView.as_view(), name='learning-path'),
]
