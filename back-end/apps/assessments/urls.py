from django.urls import path
from .views import (
    AssessmentListView,
    AssessmentDetailView,
    AssessmentSubmitView,
)

urlpatterns = [
    path('', AssessmentListView.as_view(), name='assessment-list'),
    path('<int:pk>', AssessmentDetailView.as_view(), name='assessment-detail'),
    path('<int:pk>/submit', AssessmentSubmitView.as_view(), name='assessment-submit'),
]
