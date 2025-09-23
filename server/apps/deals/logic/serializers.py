from rest_framework import serializers

from server.apps.deals.models import Deal, DealStats


class DealStatsSerializer(serializers.ModelSerializer):
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


class DealDetailResponseSerializer(serializers.ModelSerializer[Deal]):
    """Serializer for detailed Deal representation."""

    keywords = serializers.SerializerMethodField()

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
        )

    def get_keywords(self, obj: Deal) -> list[str]:
        """Convert comma-separated keywords to a list."""
        if obj.keywords:
            # Split by comma and strip whitespace from each item
            return [keyword.strip() for keyword in obj.keywords.split(',') if keyword.strip()]
        return []
