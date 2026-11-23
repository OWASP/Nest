"""Django admin configuration for ContributionScore model."""

import logging

from django.contrib import admin, messages

from apps.owasp.exceptions import CertificateIssuanceError
from apps.owasp.models.crp.contribution_score import ContributionScore
from apps.owasp.utils.score_calculator import ContributionScoreCalculator

logger: logging.Logger = logging.getLogger(__name__)


@admin.register(ContributionScore)
class ContributionScoreAdmin(admin.ModelAdmin):
    """Admin for ContributionScore model."""

    autocomplete_fields = ("github_user",)
    list_display = ("github_user", "value", "tier", "nest_updated_at")
    list_filter = ("tier", "nest_created_at")
    search_fields = ("github_user__login", "github_user__name")
    readonly_fields = ("nest_created_at", "nest_updated_at")
    actions = ("recalculate",)

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

    @admin.action(
        description="Recalculate selected contributors' scores",
        permissions=["change"],
    )
    def recalculate(self, request, queryset):
        """Admin action to recalculate scores for selected users."""
        calculator = ContributionScoreCalculator()
        updated_count = 0
        certificate_failed_count = 0
        failed_count = 0

        for score in queryset.select_related("github_user"):
            login = score.github_user.login
            try:
                calculator.recalculate_user(score.github_user)
            except CertificateIssuanceError:
                # The score is saved before certificate issuance is attempted.
                logger.exception("Failed to issue certificate for user %s", login)
                updated_count += 1
                certificate_failed_count += 1
            except Exception:
                logger.exception("Failed to recalculate score for user %s", login)
                failed_count += 1
            else:
                updated_count += 1

        message = (
            f"Recalculated scores for {updated_count} contributor(s). "
            f"Failed for {failed_count} contributor(s)."
        )
        if certificate_failed_count:
            message += (
                f" Certificate issuance failed for {certificate_failed_count} contributor(s)."
            )

        self.message_user(
            request,
            message,
            level=messages.WARNING if failed_count or certificate_failed_count else messages.INFO,
        )
