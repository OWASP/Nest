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
        "winner_name",
        "user",
        "is_reviewed",
        "nest_created_at",
        "nest_updated_at",
    )
    list_display_links = ("name", "winner_name")
    list_per_page = 50
    list_filter = (
        "category",
        "year",
        "is_reviewed",
    )
    search_fields = (
        "name",
        "winner_name",
        "description",
        "winner_info",
        "user__login",
    )
    ordering = ("-year", "category", "name")

    autocomplete_fields = ("user",)
    actions = ("mark_reviewed", "mark_not_reviewed")
    list_select_related = ("user",)

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "category", "year", "description")},
        ),
        (
            "Winner Information",
            {
                "fields": (
                    "winner_name",
                    "winner_info",
                    "winner_image_url",
                    "user",
                    "is_reviewed",
                ),
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

    @admin.action(description="Mark selected awards as reviewed")
    def mark_reviewed(self, request, queryset):
        """Mark selected awards as reviewed."""
        updated = queryset.update(is_reviewed=True)
        self.message_user(request, f"Marked {updated} award(s) as reviewed.")

    @admin.action(description="Mark selected awards as not reviewed")
    def mark_not_reviewed(self, request, queryset):
        """Mark selected awards as not reviewed."""
        updated = queryset.update(is_reviewed=False)
        self.message_user(request, f"Marked {updated} award(s) as not reviewed.")
