from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import BlockchainCredential, DemoAnchor
from .serializers import BlockchainProofSerializer, DemoAnchorSerializer
from apps.credentials.models import Credential
from apps.common.throttling import DemoAnchorBudget
from .demo_anchor import DemoAnchorError, queue_demo_anchor


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


class DemoAnchorView(APIView):
    """Queue/read a Base Sepolia digest transaction for the authenticated owner's draft demo."""
    permission_classes = [IsAuthenticated]
    throttle_classes = [DemoAnchorBudget]
    serializer_class = DemoAnchorSerializer

    def get_object(self, request, credential_id):
        return get_object_or_404(DemoAnchor, credential_id=credential_id,
            credential__user=request.user, credential__status=Credential.Status.DRAFT,
            credential__metadata__mode='demo')

    @extend_schema(summary='Queue Base Sepolia demo anchor', responses={202: DemoAnchorSerializer})
    def post(self, request, credential_id):
        credential = get_object_or_404(Credential, pk=credential_id, user=request.user,
            status=Credential.Status.DRAFT, metadata__mode='demo')
        try:
            anchor = queue_demo_anchor(credential)
        except DemoAnchorError as exc:
            code = str(exc)
            if code == 'signer_not_configured':
                return Response({'detail': 'Demo anchoring is not configured.', 'code': code}, status=503)
            return Response({'detail': 'Unable to queue demo anchor.', 'code': code}, status=400)
        return Response(DemoAnchorSerializer(anchor).data, status=status.HTTP_202_ACCEPTED)

    @extend_schema(summary='Read Base Sepolia demo anchor', responses={200: DemoAnchorSerializer})
    def get(self, request, credential_id):
        return Response(DemoAnchorSerializer(self.get_object(request, credential_id)).data)
