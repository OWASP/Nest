"""Nest app admin."""

from django.contrib import admin

from apps.nest.models.api_key import ApiKey
from apps.nest.models.user import User


class UserAdmin(admin.ModelAdmin):
    """Admin for User model."""

    ordering = ("username",)
    search_fields = ("email", "username")


class ApiKeyAdmin(admin.ModelAdmin):
    """Admin for ApiKey model."""

    autocomplete_fields = ("user",)
    list_display = (
        "name",
        "user",
        "uuid",
        "is_revoked",
        "expires_at",
        "created_at",
        "last_used_at",
    )
    list_filter = ("is_revoked",)
    ordering = ("-created_at",)
    search_fields = (
        "name",
        "uuid",
        "user__username",
    )


admin.site.register(ApiKey, ApiKeyAdmin)
admin.site.register(User, UserAdmin)
