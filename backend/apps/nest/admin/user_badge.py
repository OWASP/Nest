"""Admin configuration for the user badge model in the OWASP app."""

from django.contrib import admin

from apps.nest.models.user_badge import UserBadge


class UserBadgeAdmin(admin.ModelAdmin):
    """Admin for UserBadge model."""

    autocomplete_fields = ("user", "badge")
    fieldsets = (
        (
            "User and Badge",
            {
                "fields": (
                    "user",
                    "badge",
                )
            },
        ),
        ("Note", {"fields": ("note",)}),
        (
            "Timestamps",
            {
                "fields": (
                    "nest_created_at",
                    "nest_updated_at",
                )
            },
        ),
    )
    list_display = (
        "user",
        "badge",
        "note",
        "nest_created_at",
        "nest_updated_at",
    )
    readonly_fields = (
        "nest_created_at",
        "nest_updated_at",
    )
    search_fields = ("user__login", "badge__name", "note")


admin.site.register(UserBadge, UserBadgeAdmin)
