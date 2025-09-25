from rest_framework import serializers

from server.apps.main.models import CommunityStats, Promotions


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


class PromotionsSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    image_background = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Promotions
        fields = (
            'uuid',
            'title',
            'content',
            'image_background',
            'cta_url',
            'created_by',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('uuid', 'created_by', 'created_at', 'updated_at')
