"""Django admin screen for Slack reaction rules."""

from django.contrib import admin

from apps.slack.models.reaction_rule import ReactionRule


@admin.register(ReactionRule)
class ReactionRuleAdmin(admin.ModelAdmin):
    """Admin list/search controls for reaction rules."""

    autocomplete_fields = ("conversation",)
    list_display = (
        "conversation",
        "emojis",
        "report_type",
        "threshold",
        "is_active",
    )
    list_filter = (
        "is_active",
        "report_type",
    )
    search_fields = (
        "conversation__name",
        "alert_channel_id",
    )
