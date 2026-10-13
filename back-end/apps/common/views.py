import uuid
from django.conf import settings
from django.core.cache import caches
from django.db import connection
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import HealthCheckResponseSerializer, ReadinessResponseSerializer


class HealthCheckView(APIView):
    """Health check endpoint to verify backend system status."""
    permission_classes = [AllowAny]

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


class ReadinessView(APIView):
    """Checks local dependencies without spending external provider quota."""
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Backend readiness',
        description='Checks the database, configured throttle cache and minimum demo catalog.',
        tags=['System'],
        responses={
            200: ReadinessResponseSerializer,
            503: OpenApiResponse(response=ReadinessResponseSerializer, description='A required dependency is unavailable.'),
        },
    )
    def get(self, request, *args, **kwargs):
        components = {'database': 'ok', 'cache': 'ok', 'catalog': 'ok'}
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
        except Exception:
            components['database'] = 'unavailable'

        cache_key = f'readiness:{uuid.uuid4()}'
        cache = None
        try:
            cache = caches[settings.THROTTLE_CACHE_ALIAS]
            marker = uuid.uuid4().hex
            cache.set(cache_key, marker, timeout=5)
            if cache.get(cache_key) != marker:
                components['cache'] = 'unavailable'
        except Exception:
            components['cache'] = 'unavailable'
        finally:
            if cache is not None:
                try:
                    cache.delete(cache_key)
                except Exception:
                    components['cache'] = 'unavailable'

        try:
            from apps.assessments.models import Assessment, DiagnosticQuestion
            from apps.careers.models import CareerTrack
            from apps.skills.models import Skill
            catalog_ready = (
                CareerTrack.objects.filter(is_active=True).exists()
                and Skill.objects.filter(competency__career_track__is_active=True).values('pk').distinct().count() >= 2
                and Assessment.objects.filter(skill__competency__career_track__is_active=True).exists()
                and DiagnosticQuestion.objects.filter(is_active=True).exists()
            )
            if not catalog_ready:
                components['catalog'] = 'unavailable'
        except Exception:
            components['catalog'] = 'unavailable'

        ready = all(value == 'ok' for value in components.values())
        return Response(
            {'status': 'ready' if ready else 'not_ready', 'components': components},
            status=status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        )
