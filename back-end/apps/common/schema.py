"""OpenAPI fragments shared by endpoints that spend a request budget."""
from rest_framework import serializers
from drf_spectacular.utils import OpenApiExample, OpenApiResponse


class ThrottledResponseSerializer(serializers.Serializer):
    """Body of every ``429`` this API returns."""

    detail = serializers.CharField(
        help_text='Human readable explanation, including the wait in seconds.'
    )
    retry_after_seconds = serializers.IntegerField(
        help_text='Seconds to wait; identical to the Retry-After header.'
    )


THROTTLED_RESPONSE = {
    429: OpenApiResponse(
        response=ThrottledResponseSerializer,
        description=(
            'The request budget for this endpoint is exhausted. The same wait '
            'is reported in the Retry-After header and in retry_after_seconds.'
        ),
        examples=[OpenApiExample(
            'Throttled',
            value={
                'detail': 'Request was throttled. Expected available in 42 seconds.',
                'retry_after_seconds': 42,
            },
        )],
    )
}