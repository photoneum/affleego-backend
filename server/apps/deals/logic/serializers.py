from rest_framework import serializers

from server.apps.deals.models import Deal, DealStats


class DealDetailResponseSerializer(serializers.ModelSerializer[Deal]):
    """Serializer for detailed Deal representation."""

    keywords = serializers.SerializerMethodField()
    logo_url = serializers.ImageField(source='logo', required=False, allow_null=True)

    class Meta:
        model = Deal
        fields = (
            'uuid',
            'name',
            'requirements',
            'commission_type',
            'projected_payout',
            'revenue_share',
            'payout_schedule',
            'status',
            'is_featured',
            'referral_link',
            'description',
            'keywords',
            'logo_url',
        )

    def get_keywords(self, obj: Deal) -> list[str]:
        """Convert comma-separated keywords to a list."""
        if obj.keywords:
            # Split by comma and strip whitespace from each item
            return [keyword.strip() for keyword in obj.keywords.split(',') if keyword.strip()]
        return []


class DealStatsSerializer(serializers.ModelSerializer):
    deal = DealDetailResponseSerializer(read_only=True)

    class Meta:
        model = DealStats
        fields = (
            'uuid',
            'deal',
            'period_start',
            'period_end',
            'clicks',
            'impressions',
        )
        read_only_fields = ('uuid', 'created_at', 'updated_at')


class DealStatsOverviewSerializer(serializers.Serializer):
    """Serializer for deal stats overview response.

    Returns statistics for featured, hot, and all deals, including week period.
    """

    featured_deals = serializers.IntegerField()
    hot_deals = serializers.IntegerField()
    week_start = serializers.DateField()
    week_end = serializers.DateField()
    all_deals = serializers.IntegerField()
