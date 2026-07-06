"""Django admin screen for emitted Slack reaction alerts."""

from django.contrib import admin

from apps.slack.models.reaction_alert import ReactionAlert


@admin.register(ReactionAlert)
class ReactionAlertAdmin(admin.ModelAdmin):
    """Admin list/search controls for emitted reaction alerts."""

    list_display = (
        "conversation",
        "message_ts",
        "report_type",
        "reaction_count",
        "nest_created_at",
    )
    search_fields = ("conversation__name", "message_ts", "report_type")
    readonly_fields = (
        "conversation",
        "message_ts",
        "report_type",
        "reaction_count",
        "alert_message_ts",
    )

    def has_add_permission(self, request):
        """Disable manual alert creation in Django admin."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable manual alert deletion in Django admin."""
        return False
