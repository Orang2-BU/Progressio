from django.urls import path
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.common.schema import THROTTLED_RESPONSE
from apps.common.throttling import (
    AuthLoginAddressThrottle,
    AuthLoginThrottle,
    AuthRefreshThrottle,
)

from .views import RegisterView, MeView


class ThrottledTokenObtainPairView(TokenObtainPairView):
    """Token login, budgeted per attempted account and client address."""

    throttle_classes = [AuthLoginThrottle, AuthLoginAddressThrottle]

    @extend_schema(
        summary="Login",
        description="Exchange credentials for an access and a refresh token.",
        tags=["Authentication"],
        responses={
            200: OpenApiResponse(
                response=TokenObtainPairView.serializer_class,
                description="Tokens issued.",
            ),
            **THROTTLED_RESPONSE,
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ThrottledTokenRefreshView(TokenRefreshView):
    """Token refresh, budgeted per client address so no token enters a key."""

    throttle_classes = [AuthRefreshThrottle]

    @extend_schema(
        summary="Refresh access token",
        description="Exchange a refresh token for a new access token.",
        tags=["Authentication"],
        responses={
            200: OpenApiResponse(
                response=TokenRefreshView.serializer_class,
                description="New access token issued.",
            ),
            **THROTTLED_RESPONSE,
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


urlpatterns = [
    path('register', RegisterView.as_view(), name='auth-register'),
    path('login', ThrottledTokenObtainPairView.as_view(), name='auth-login'),
    path('refresh', ThrottledTokenRefreshView.as_view(), name='auth-refresh'),
    path('me', MeView.as_view(), name='auth-me'),
]
