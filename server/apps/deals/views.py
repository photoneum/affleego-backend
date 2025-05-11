from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from server.apps.deals.logic.serializers import DealDetailResponseSerializer
from server.apps.deals.models import Deal
from server.common.api_response import ApiResponse


@extend_schema(tags=['Deals'])
class DealViewSet(viewsets.ModelViewSet):
    """ViewSet for managing deals."""

    queryset = Deal.objects.all()
    serializer_class = DealDetailResponseSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: DealDetailResponseSerializer(many=True)},
        description='List all available deals',
        summary='List Deals',
    )
    def list(self, request: Request) -> Response:
        """List all deals."""
        deals = self.get_queryset()
        serializer = self.get_serializer(deals, many=True)
        return ApiResponse(
            data=serializer.data,
            message='Deals retrieved successfully',
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses={200: DealDetailResponseSerializer},
        description='Get detailed information about a specific deal',
        summary='Get Deal',
    )
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Retrieve a specific deal."""
        deal = self.get_object()
        serializer = self.get_serializer(deal)
        return ApiResponse(
            data=serializer.data,
            message='Deal retrieved successfully',
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses={200: DealDetailResponseSerializer(many=True)},
        description='List featured deals',
        summary='Featured Deals',
    )
    @action(detail=False, methods=['get'])
    def featured(self, request: Request) -> Response:
        """List featured deals."""
        featured_deals = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(featured_deals, many=True)
        return ApiResponse(
            data=serializer.data,
            message='Featured deals retrieved successfully',
            status=status.HTTP_200_OK,
        )
