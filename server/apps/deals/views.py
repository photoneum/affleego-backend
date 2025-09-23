from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from server.apps.deals.logic.serializers import (
    DealDetailResponseSerializer,
    DealStatsSerializer,
)
from server.apps.deals.models import Deal, DealStats
from server.common.api_response import ApiResponse


@extend_schema(tags=['Deals'])
class DealViewSet(viewsets.ModelViewSet):
    """ViewSet for managing deals."""

    queryset = Deal.objects.all()
    serializer_class = DealDetailResponseSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Get top performing deals of the week',
        responses={200: DealStatsSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], url_path='top')
    def top(self, request: Request) -> Response:
        """Get top performing deals for the current week."""
        from datetime import timedelta

        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        stats_qs = DealStats.objects.filter(
            period_start__gte=start_of_week,
            period_end__lte=end_of_week,
        ).order_by('-clicks')[:10]
        serializer = DealStatsSerializer(stats_qs, many=True)
        return ApiResponse(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Record a click for a deal',
        responses={200: ApiResponse},
    )
    @action(detail=True, methods=['post'], url_path='click')
    def record_click(self, request: Request, pk=None) -> Response:
        """Record a click event for a deal."""
        deal = self.get_object()
        today = timezone.now().date()
        stats, _ = DealStats.objects.get_or_create(
            deal=deal,
            period_start=today,
            period_end=today,
        )
        stats.clicks += 1
        stats.save()
        return ApiResponse('Click recorded.')

    @extend_schema(
        summary='Record an impression for a deal',
        responses={200: ApiResponse},
    )
    @action(detail=True, methods=['post'], url_path='impression')
    def record_impression(self, request: Request, pk=None) -> Response:
        """Record an impression event for a deal."""
        deal = self.get_object()
        today = timezone.now().date()
        stats, _ = DealStats.objects.get_or_create(
            deal=deal,
            period_start=today,
            period_end=today,
        )
        stats.impressions += 1
        stats.save()
        return ApiResponse('Impression recorded.')

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
