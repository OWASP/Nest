"""Nest app admin."""

from django.contrib import admin

from apps.nest.models.api_key import ApiKey
from apps.nest.models.user import User


class UserAdmin(admin.ModelAdmin):
    ordering = ("username",)
    search_fields = ("email", "username")


class ApiKeyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "public_id",
        "is_revoked",
        "expires_at",
        "created_at",
        "last_used_at",
    )
    list_filter = (
        "expires_at",
        "created_at",
        "last_used_at",
    )
    ordering = ("-created_at",)
    search_fields = (
        "name",
        "public_id",
        "user__username",
    )


admin.site.register(ApiKey, ApiKeyAdmin)

admin.site.register(User, UserAdmin)
