from django.urls import path
from .views import (
    CredentialListView,
    CredentialDetailView,
    CredentialIssueView,
)

urlpatterns = [
    path('', CredentialListView.as_view(), name='credential-list'),
    path('issue', CredentialIssueView.as_view(), name='credential-issue'),
    path('<uuid:pk>', CredentialDetailView.as_view(), name='credential-detail'),
]
