from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from server.apps.main.logic.serializers import CommunityStatsSerializer
from server.apps.main.models import CommunityStats
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
