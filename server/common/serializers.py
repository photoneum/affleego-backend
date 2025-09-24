from rest_framework import serializers


class ApiResponseSerializer(serializers.Serializer):
    """Serializer for documenting ApiResponse structure."""

    data = serializers.JSONField(required=False)  # type: ignore
    message = serializers.CharField(required=False)
    status = serializers.IntegerField(required=False)
    state = serializers.CharField(required=False)


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for documenting ErrorResponse structure."""

    data = serializers.JSONField(required=False)  # type: ignore
    message = serializers.CharField(required=False)
    status = serializers.IntegerField(required=False)
    state = serializers.CharField(required=False)
    detail = serializers.CharField(required=False)
