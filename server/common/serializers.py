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


class PaginationMetadataSerializer(serializers.Serializer):
    """Serializer for pagination metadata."""

    current_page = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_count = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()
    next_page = serializers.IntegerField(allow_null=True)
    previous_page = serializers.IntegerField(allow_null=True)
