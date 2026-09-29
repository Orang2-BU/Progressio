from django.urls import path
from .views import (
    CredentialListView,
    CredentialDetailView,
    CredentialIssueView,
    CredentialEligibilityView,
)

urlpatterns = [
    path('eligibility/<int:pk>', CredentialEligibilityView.as_view(), name='credential-eligibility'),
    path('', CredentialListView.as_view(), name='credential-list'),
    path('issue', CredentialIssueView.as_view(), name='credential-issue'),
    path('<uuid:pk>', CredentialDetailView.as_view(), name='credential-detail'),
]
