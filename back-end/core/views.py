from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import HealthCheckResponseSerializer


class HealthCheckView(APIView):
    """
    Health check endpoint to verify backend system status and connectivity.
    """
    permission_classes = []

    @extend_schema(
        summary="API Health Check",
        description="Returns the current operational status of the Progressio backend API.",
        tags=["System"],
        responses={
            200: OpenApiResponse(
                response=HealthCheckResponseSerializer,
                description="Backend is healthy and operational."
            )
        }
    )
    def get(self, request, *args, **kwargs):
        data = {
            "status": "ok",
            "service": "Progressio API",
            "version": "1.0.0",
            "message": "Progressio backend service is running smoothly."
        }
        return Response(data, status=status.HTTP_200_OK)
