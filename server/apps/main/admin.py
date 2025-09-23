from django.contrib import admin

from server.apps.main.models import CommunityStats


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
