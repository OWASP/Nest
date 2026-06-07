"""Django admin configuration for ContributionScore model."""

from django.contrib import admin

from apps.owasp.models.contribution_score import ContributionScore
from apps.owasp.score_calculator import ContributionScoreCalculator


@admin.register(ContributionScore)
class ContributionScoreAdmin(admin.ModelAdmin):
    """Admin for ContributionScore model."""

    autocomplete_fields = ("github_user",)
    list_display = ("github_user", "value", "tier", "nest_updated_at")
    list_filter = ("tier", "nest_created_at")
    search_fields = ("github_user__login", "github_user__name")
    readonly_fields = ("nest_created_at", "nest_updated_at")
    actions = ("recalculate_score",)

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
                "fields": ("value", "tier"),
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

    def recalculate_score(self, request, queryset):
        """Admin action to recalculate scores for selected users."""
        calculator = ContributionScoreCalculator()
        updated_count = 0
        failed_count = 0

        for score_obj in queryset:
            try:
                calculator.recalculate_user_score(score_obj.github_user)
                updated_count += 1
            except (ValueError, TypeError):
                failed_count += 1

        self.message_user(
            request,
            f"Recalculated scores for {updated_count} contributor(s). "
            f"Failed for {failed_count} contributor(s).",
        )

    recalculate_score.short_description = "Recalculate selected contributors' scores"
