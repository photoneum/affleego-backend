# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from server.apps.users import models


@admin.register(models.User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_superuser',
        'uuid',
    )
    ordering = ('-date_joined',)
    search_fields = (
        'email',
        'first_name',
        'last_name',
    )
    readonly_fields = (
        'uuid',
        'date_joined',
        'last_login',
    )
    fieldsets = (
        *UserAdmin.fieldsets,  # type: ignore
        (
            'Other Information',
            {
                'fields': (
                    'is_verified',
                    'image',
                ),
            },
        ),
    )


@admin.register(models.VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'is_used', 'created_at', 'expires_at')
    search_fields = ('code', 'user__email')
    list_filter = ('is_used',)
