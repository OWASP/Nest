"""Award admin configuration."""

from django.contrib import admin

from apps.owasp.models.award import Award


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    """Admin for Award model."""

    list_display = (
        "name",
        "category",
        "year",
        "award_type",
        "winner_name",
        "user",
        "nest_created_at",
        "nest_updated_at",
    )
    list_filter = (
        "award_type",
        "category",
        "year",
    )
    search_fields = (
        "name",
        "category",
        "winner_name",
        "description",
        "winner_info",
    )
    ordering = ("-year", "category", "name")

    autocomplete_fields = ("user",)

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "category", "award_type", "year", "description")},
        ),
        (
            "Winner Information",
            {
                "fields": ("winner_name", "winner_info", "winner_image", "user"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("nest_created_at", "nest_updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("nest_created_at", "nest_updated_at")

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related("user")
