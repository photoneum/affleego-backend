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
class PromotionsViewSet(viewsets.GenericViewSet):
    queryset = Promotions.objects.all()
    serializer_class = PromotionsSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description='List all promotions',
        summary='List promotions',
        responses={200: PromotionsSerializer(many=True)},
    )
    def list(self, request: Request) -> Response:
        """List all promotions."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse(serializer.data, status=status.HTTP_200_OK)

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
        responses={201: PromotionsSerializer},
    )
    def create(self, request: Request) -> Response:
        """Create a new promotion."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return ApiResponse(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description='Retrieve a specific promotion by UUID',
        summary='Get promotion',
        responses={200: PromotionsSerializer},
    )
    def retrieve(self, request: Request, pk: str) -> Response:
        """Retrieve a specific promotion by UUID."""
        promotion = self.get_object()
        serializer = self.get_serializer(promotion)
        return ApiResponse(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description='Update a promotion',
        summary='Update promotion',
        responses={200: PromotionsSerializer},
    )
    def update(self, request: Request, pk: str) -> Response:
        """Update a promotion."""
        promotion = self.get_object()
        serializer = self.get_serializer(promotion, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ApiResponse(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description='Partially update a promotion',
        summary='Partial update promotion',
        responses={200: PromotionsSerializer},
    )
    def partial_update(self, request: Request, pk: str) -> Response:
        """Partially update a promotion."""
        promotion = self.get_object()
        serializer = self.get_serializer(promotion, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ApiResponse(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description='Delete a promotion',
        summary='Delete promotion',
        responses={204: None},
    )
    def destroy(self, request: Request, pk: str) -> Response:
        """Delete a promotion."""
        promotion = self.get_object()
        promotion.delete()
        return ApiResponse(None, status=status.HTTP_204_NO_CONTENT)
