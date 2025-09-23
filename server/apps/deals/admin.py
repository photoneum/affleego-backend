from django.contrib import admin

from server.apps.deals.models import Deal, DealStats


@admin.register(DealStats)
class DealStatsAdmin(admin.ModelAdmin):
    list_display = ('deal', 'period_start', 'period_end', 'clicks', 'impressions')


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'created_by')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
