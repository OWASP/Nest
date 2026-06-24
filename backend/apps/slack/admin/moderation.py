"""Django admin screens for Slack moderation configuration.

Admins use rules to enable per-channel reaction thresholds, and alerts are
readonly-ish records showing which message/report pairs already notified.
"""

from django.contrib import admin

from apps.slack.models.moderation import ModerationAlert, ModerationRule


@admin.register(ModerationRule)
class ModerationRuleAdmin(admin.ModelAdmin):
    """Admin list/search controls for moderation rules."""

    list_display = ("conversation", "emoji_name", "report_type", "threshold", "is_enabled")
    list_filter = ("is_enabled", "report_type")
    search_fields = ("conversation__name", "emoji_name", "alert_channel_id")


@admin.register(ModerationAlert)
class ModerationAlertAdmin(admin.ModelAdmin):
    """Admin list/search controls for emitted moderation alerts."""

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
