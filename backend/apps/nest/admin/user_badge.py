"""Admin configuration for the user badge model in the OWASP app."""

from django.contrib import admin

from apps.nest.models.user_badge import UserBadge


class UserBadgeAdmin(admin.ModelAdmin):
    """Admin for UserBadge model."""

    autocomplete_fields = (
        "badge",
        "user",
    )
    list_display = (
        "user",
        "badge",
        "note",
        "nest_created_at",
        "nest_updated_at",
    )
    list_filter = ("is_active", "badge__name")
    readonly_fields = (
        "nest_created_at",
        "nest_updated_at",
    )
    search_fields = (
        "badge__name",
        "note",
        "user__login",
        "user__name",
    )


admin.site.register(UserBadge, UserBadgeAdmin)
