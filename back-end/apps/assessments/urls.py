from django.urls import path
from .views import (
    AssessmentListView,
    AssessmentDetailView,
    AssessmentSubmitView,
    SubmissionListView,
    SubmissionDetailView,
)

urlpatterns = [
    path('submissions/', SubmissionListView.as_view(), name='submission-list'),
    path('submissions/<int:pk>', SubmissionDetailView.as_view(), name='submission-detail'),
    path('', AssessmentListView.as_view(), name='assessment-list'),
    path('<int:pk>', AssessmentDetailView.as_view(), name='assessment-detail'),
    path('<int:pk>/submit', AssessmentSubmitView.as_view(), name='assessment-submit'),
]
