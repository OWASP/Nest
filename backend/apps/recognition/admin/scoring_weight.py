"""Django admin configuration for ScoringWeight model."""

from django.contrib import admin

from apps.recognition.models.scoring_weight import ScoringWeight


@admin.register(ScoringWeight)
class ScoringWeightAdmin(admin.ModelAdmin):
    """Admin for ScoringWeight model."""

    list_display = ("event_type", "score", "daily_cap", "is_active", "nest_updated_at")
    list_filter = ("event_type", "is_active", "nest_created_at")
    search_fields = ("event_type",)
    readonly_fields = ("nest_created_at", "nest_updated_at")

    fieldsets = (
        (
            "Contribution Weight",
            {
                "fields": ("event_type", "score", "daily_cap", "is_active"),
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
