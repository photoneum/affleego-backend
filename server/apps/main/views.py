from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from server.apps.main.logic.serializers import CommunityStatsSerializer
from server.apps.main.models import CommunityStats
from server.apps.users.logic.serializers import UserProfileSerializer
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
        user = request.user
        # Get latest community stats
        stats = CommunityStats.objects.order_by('-week_starting').first()
        stats_data = CommunityStatsSerializer(stats).data if stats else None
        user_data = UserProfileSerializer(user).data
        last_login = getattr(user, 'last_login', None)
        overview = {
            'user': user_data,
            'community_stats': stats_data,
            'last_login': last_login,
        }
        return ApiResponse(overview, status=status.HTTP_200_OK)
