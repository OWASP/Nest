"""API key model admin."""

from django.contrib import admin

from apps.api.models.api_key import ApiKey


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
