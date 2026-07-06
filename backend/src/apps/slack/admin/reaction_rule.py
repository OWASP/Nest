"""Django admin screen for Slack reaction rules."""

from django.contrib import admin

from apps.slack.models.reaction_rule import ReactionRule


@admin.register(ReactionRule)
class ReactionRuleAdmin(admin.ModelAdmin):
    """Admin list/search controls for reaction rules."""

    list_display = ("conversation", "emoji_name", "report_type", "threshold", "is_enabled")
    list_filter = ("is_enabled", "report_type")
    search_fields = ("conversation__name", "emoji_name", "alert_channel_id")
