from django.urls import path
from .views import BlockchainProofDetailView

urlpatterns = [
    path('proof/<uuid:credential_id>', BlockchainProofDetailView.as_view(), name='blockchain-proof-detail'),
]
