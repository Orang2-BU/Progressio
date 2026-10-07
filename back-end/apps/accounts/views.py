from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.common.schema import THROTTLED_RESPONSE
from apps.common.throttling import AuthRegisterThrottle

from .serializers import UserRegistrationSerializer, UserProfileSerializer


class RegisterView(generics.CreateAPIView):
    """Register a new user account."""
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthRegisterThrottle]

    @extend_schema(
        summary="Register",
        description="Create a new user account.",
        tags=["Authentication"],
        responses={
            201: OpenApiResponse(
                response=UserProfileSerializer,
                description="User registered successfully."
            ),
            **THROTTLED_RESPONSE,
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        profile = UserProfileSerializer(user)
        return Response(profile.data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    """Get the current authenticated user's profile."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Current User Profile",
        description="Returns the profile of the currently authenticated user.",
        tags=["Authentication"],
        responses={
            200: OpenApiResponse(
                response=UserProfileSerializer,
                description="Current user profile."
            )
        }
    )
    def get(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
