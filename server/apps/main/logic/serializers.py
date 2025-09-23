from rest_framework import serializers

from server.apps.main.models import CommunityStats


class CommunityStatsSerializer(serializers.ModelSerializer):
    total_affiliates = serializers.SerializerMethodField(read_only=True)
    total_deals = serializers.SerializerMethodField(read_only=True)

    def get_total_affiliates(self, obj):
        from server.apps.users.logic.serializers import User

        return User.objects.filter(is_active=True).count()

    def get_total_deals(self, obj):
        from server.apps.deals.models import Deal

        return Deal.objects.count()

    class Meta:
        model = CommunityStats
        fields = (
            'uuid',
            'weekly_ftds',
            'top_geo',
            'total_affiliates',
            'total_deals',
            'week_starting',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('uuid', 'created_at', 'updated_at')
