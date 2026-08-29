from rest_framework import serializers


class HealthCheckResponseSerializer(serializers.Serializer):
    status = serializers.CharField(default="ok", help_text="Status of the API service")
    service = serializers.CharField(default="Progressio API", help_text="Service name")
    version = serializers.CharField(default="1.0.0", help_text="API Version")
    message = serializers.CharField(default="Progressio backend service is running smoothly.", help_text="Status message")
