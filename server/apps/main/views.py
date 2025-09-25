from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from server.apps.main.logic.serializers import (
    CommunityStatsSerializer,
    PromotionsSerializer,
)
from server.apps.main.models import CommunityStats, Promotions
from server.common.api_response import ApiResponse


@extend_schema(tags=['Dashboard'])
class DashboardViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: CommunityStatsSerializer},
        description='Get dashboard overview data including user greeting and community stats',
        summary='Dashboard Overview',
    )
    @action(detail=False, methods=['get'])
    def overview(self, request: Request) -> Response:
        # Get latest community stats
        stats = CommunityStats.objects.order_by('-week_starting').first()
        stats_data = CommunityStatsSerializer(stats).data if stats else None

        return ApiResponse(stats_data, status=status.HTTP_200_OK)


@extend_schema(tags=['Promotions'])
class PromotionsViewSet(viewsets.ModelViewSet):
    queryset = Promotions.objects.all()
    serializer_class = PromotionsSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)

    @extend_schema(
        description='List all promotions',
        summary='List promotions',
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description='Create a new promotion',
        summary='Create promotion',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': 'Title of the promotion'},
                    'content': {'type': 'string', 'description': 'Content of the promotion'},
                    'image_background': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Background image file (optional)',
                        'nullable': True,
                    },
                    'cta_url': {
                        'type': 'string',
                        'format': 'uri',
                        'description': 'Call-to-action URL',
                    },
                },
                'required': ['title', 'content', 'cta_url'],
            }
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return ApiResponse(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(
        description='Retrieve a specific promotion by UUID',
        summary='Get promotion',
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description='Update a promotion',
        summary='Update promotion',
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description='Partially update a promotion',
        summary='Partial update promotion',
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description='Delete a promotion',
        summary='Delete promotion',
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
