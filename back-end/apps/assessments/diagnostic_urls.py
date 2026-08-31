from django.urls import path

from .diagnostic_views import (
    DiagnosticQuestionListView,
    DiagnosticSubmitView,
    LatestDiagnosticAttemptView,
)


urlpatterns = [
    path('latest', LatestDiagnosticAttemptView.as_view(), name='diagnostic-latest'),
    path('<int:career_track_id>', DiagnosticQuestionListView.as_view(), name='diagnostic-question-list'),
    path('<int:career_track_id>/submit', DiagnosticSubmitView.as_view(), name='diagnostic-submit'),
]
