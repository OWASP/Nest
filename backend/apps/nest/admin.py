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
        "key_suffix",
        "is_revoked",
        "expires_at",
        "created_at",
    )
    list_filter = (
        "is_revoked",
        "expires_at",
        "created_at",
    )
    ordering = ("-created_at",)
    search_fields = (
        "name",
        "user__username",
        "key_suffix",
    )


admin.site.register(ApiKey, ApiKeyAdmin)

admin.site.register(User, UserAdmin)
