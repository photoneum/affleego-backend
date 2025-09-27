from django.contrib import admin

from server.apps.main.models import CommunityStats, Promotions


@admin.register(CommunityStats)
class CommunityStatsAdmin(admin.ModelAdmin[CommunityStats]):
    list_display = (
        'uuid',
        'weekly_ftds',
        'top_geo',
        'week_starting',
        'created_at',
        'updated_at',
    )
    search_fields = ('top_geo',)
    list_filter = ('week_starting',)


@admin.register(Promotions)
class PromotionsAdmin(admin.ModelAdmin[Promotions]):
    list_display = (
        'uuid',
        'title',
        'created_by',
        'cta_url',
        'created_at',
        'updated_at',
    )
    search_fields = ('title', 'content')
    list_filter = ('created_at', 'created_by')
    readonly_fields = ('uuid', 'created_at', 'updated_at')
