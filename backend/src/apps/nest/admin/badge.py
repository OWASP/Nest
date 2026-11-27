"""Admin configuration for the Badge model in the OWASP app."""

from django.contrib import admin

from apps.nest.models.badge import Badge


class BadgeAdmin(admin.ModelAdmin):
    """Admin for Badge model."""

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "description",
                    "weight",
                )
            },
        ),
        ("Display Settings", {"fields": ("css_class",)}),
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
        "name",
        "description",
        "weight",
        "css_class",
        "nest_created_at",
        "nest_updated_at",
    )
    list_filter = ("weight",)
    ordering = (
        "weight",
        "name",
    )
    readonly_fields = (
        "nest_created_at",
        "nest_updated_at",
    )
    search_fields = (
        "css_class",
        "description",
        "name",
    )


admin.site.register(Badge, BadgeAdmin)
