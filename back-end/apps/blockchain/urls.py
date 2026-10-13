from django.urls import path
from .views import BlockchainProofDetailView, DemoAnchorView

urlpatterns = [
    path('proof/<uuid:credential_id>', BlockchainProofDetailView.as_view(), name='blockchain-proof-detail'),
    path('demo-anchors/<uuid:credential_id>', DemoAnchorView.as_view(), name='demo-anchor-detail'),
]
