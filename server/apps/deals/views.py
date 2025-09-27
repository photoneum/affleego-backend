from datetime import timedelta

from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from server.apps.deals.logic.serializers import (
    DealDetailResponseSerializer,
    DealPaginatedResponseSerializer,
    DealStatsOverviewSerializer,
    DealStatsPaginatedResponseSerializer,
    DealStatsSerializer,
)
from server.apps.deals.models import Deal, DealStats
from server.common.api_response import ApiResponse
from server.common.serializers import ApiResponseSerializer
from server.common.utils.pagination import PaginationHelper


@extend_schema(tags=['Deals Stats'])
class DealStatsViewSet(viewsets.ViewSet):
    """ViewSet for deal stats actions (top deals, click, impression)."""

    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    @extend_schema(
        responses={200: DealStatsPaginatedResponseSerializer},
        description=(
            'Get top performing deals of the week with pagination and ordering. Returns paginated '
            'results with metadata including current page, total pages, and navigation information.'
        ),
        summary='Top Performing Deals',
        parameters=[
            OpenApiParameter(
                name='page',
                description='Page number',
                required=False,
                type=int,
                default=1,
            ),
            OpenApiParameter(
                name='page_size',
                description='Number of deals per page',
                required=False,
                type=int,
                default=10,
            ),
        ],
    )
    @action(detail=False, methods=['get'], url_path='top')
    def top(self, request: Request) -> Response:
        """Get top performing deals of the week with pagination and ordering."""
        # Get query parameters with defaults
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))

        # Get current week stats
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        stats_qs = (
            DealStats.objects.filter(
                period_start__gte=start_of_week,
                period_end__lte=end_of_week,
            )
            .order_by('deal', '-clicks', '-impressions')
            .distinct('deal')
        )

        # Use PaginationHelper to handle pagination
        pagination_data, is_valid_page = PaginationHelper.paginate_queryset(
            queryset=stats_qs,
            page=page,
            page_size=page_size,
            serializer_class=DealStatsSerializer,
        )

        if not is_valid_page:
            return ApiResponse(
                data=None,
                message=pagination_data['error'],
                status=status.HTTP_404_NOT_FOUND,
            )

        return ApiResponse(
            data=pagination_data,
            message='Top performing deals retrieved successfully',
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'], url_path='click')
    def record_click(self, request: Request, uuid=None) -> Response:
        deal = Deal.objects.get(uuid=uuid)
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
        responses={200: ApiResponseSerializer},
    )
    @action(detail=True, methods=['post'], url_path='impression')
    def record_impression(self, request: Request, uuid=None) -> Response:
        deal = Deal.objects.get(uuid=uuid)
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
        summary='Get overview statistics for deals',
        responses={200: DealStatsOverviewSerializer},
    )
    @action(detail=False, methods=['get'], url_path='overview')
    def overview(self, request: Request) -> Response:
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Featured deals
        featured_count = Deal.objects.filter(is_featured=True).count()

        # Hot deals: deals with stats in current week and clicks > 0
        hot_deals_count = (
            DealStats.objects.filter(
                period_start__gte=start_of_week, period_end__lte=end_of_week, clicks__gt=0
            )
            .values('deal')
            .distinct()
            .count()
        )

        # All deals
        all_deals_count = Deal.objects.count()

        data = {
            'featured_deals': featured_count,
            'hot_deals': hot_deals_count,
            'week_start': str(start_of_week),
            'week_end': str(end_of_week),
            'all_deals': all_deals_count,
        }

        return ApiResponse(data, status=status.HTTP_200_OK)


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
        responses={200: DealPaginatedResponseSerializer},
        description=(
            'List featured deals with pagination and ordering. Returns paginated results with '
            'metadata including current page, total pages, and navigation information.'
        ),
        summary='Featured Deals',
        parameters=[
            OpenApiParameter(
                name='page',
                description='Page number',
                required=False,
                type=int,
                default=1,
            ),
            OpenApiParameter(
                name='page_size',
                description='Number of deals per page',
                required=False,
                type=int,
                default=10,
            ),
            OpenApiParameter(
                name='order_by',
                description='Field to order by',
                required=False,
                type=str,
                default='updated_at',
                enum=['updated_at', 'created_at', 'name'],
            ),
            OpenApiParameter(
                name='order',
                description='Order direction',
                required=False,
                type=str,
                default='desc',
                enum=['asc', 'desc'],
            ),
        ],
    )
    @action(detail=False, methods=['get'])
    def featured(self, request: Request) -> Response:
        """List featured deals with pagination and ordering."""
        # Get query parameters with defaults
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        order_by = request.query_params.get('order_by', 'updated_at')
        order = request.query_params.get('order', 'desc')

        # Validate order_by field
        allowed_fields = ['updated_at', 'created_at', 'name']
        if order_by not in allowed_fields:
            return ApiResponse(
                data=None,
                message=f'Invalid order_by field. Allowed: {", ".join(allowed_fields)}',
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Build ordering string
        ordering = f'-{order_by}' if order == 'desc' else order_by

        # Get featured deals with ordering
        featured_deals = self.get_queryset().filter(is_featured=True).order_by(ordering)

        # Use PaginationHelper to handle pagination
        pagination_data, is_valid_page = PaginationHelper.paginate_queryset(
            queryset=featured_deals,
            page=page,
            page_size=page_size,
            serializer_class=self.get_serializer_class(),
            serializer_context=self.get_serializer_context(),
        )

        if not is_valid_page:
            return ApiResponse(
                data=None,
                message=pagination_data['error'],
                status=status.HTTP_404_NOT_FOUND,
            )

        return ApiResponse(
            data=pagination_data,
            message='Featured deals retrieved successfully',
            status=status.HTTP_200_OK,
        )
