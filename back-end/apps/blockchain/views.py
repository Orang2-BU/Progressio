from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import BlockchainCredential
from .serializers import BlockchainProofSerializer


@extend_schema(tags=["Blockchain Proofs"])
class BlockchainProofDetailView(generics.RetrieveAPIView):
    """
    Public endpoint to view the immutable cryptographic blockchain proof of a credential.
    """
    serializer_class = BlockchainProofSerializer
    permission_classes = [AllowAny]
    lookup_field = 'credential_id'

    def get_object(self):
        return get_object_or_404(
            BlockchainCredential,
            credential_id=self.kwargs['credential_id']
        )

    @extend_schema(
        summary="View Blockchain Proof",
        description="Returns the on-chain SHA-256 digital signature, transaction hash, and network proof for a credential.",
        responses={
            200: OpenApiResponse(
                response=BlockchainProofSerializer,
                description="Blockchain cryptographic proof details."
            )
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
