"""Django admin configuration for ContributionScore model."""

from django.contrib import admin

from apps.recognition.models.contribution_score import ContributionScore


@admin.register(ContributionScore)
class ContributionScoreAdmin(admin.ModelAdmin):
    """Admin for ContributionScore model."""

    autocomplete_fields = ("github_user",)
    list_display = ("github_user", "total_score", "tier", "last_computed", "nest_updated_at")
    list_filter = ("tier", "nest_created_at")
    search_fields = ("github_user__login", "github_user__name")
    readonly_fields = ("last_computed", "nest_created_at", "nest_updated_at")

    fieldsets = (
        (
            "Contributor Information",
            {
                "fields": ("github_user",),
            },
        ),
        (
            "Score Data",
            {
                "fields": ("total_score", "tier", "last_computed"),
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
