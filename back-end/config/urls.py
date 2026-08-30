"""
URL configuration for Progressio Backend.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

api_v1_patterns = [
    path('auth/', include('apps.accounts.urls')),
    path('career-tracks/', include('apps.careers.urls')),
    path('competencies/', include('apps.competencies.urls')),
    path('skills/', include('apps.skills.urls')),
    path('assessments/', include('apps.assessments.urls')),
    path('credentials/', include('apps.credentials.urls')),
    path('', include('apps.verification.urls')),
    path('', include('apps.learning.urls')),
    path('', include('apps.common.urls')),
]

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # OpenAPI 3.0 Schema & UI Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API v1 endpoints
    path('api/v1/', include(api_v1_patterns)),

    # Root redirect to API Docs
    path('', RedirectView.as_view(url='/api/docs/', permanent=False)),
]
