"""Bot interaction admin configuration."""

from django.contrib import admin

from apps.slack.models.bot_interaction import BotInteraction


class BotInteractionAdmin(admin.ModelAdmin):
    """Admin for BotInteraction model."""

    fieldsets = (
        (
            "Interaction",
            {
                "fields": (
                    "channel_id",
                    "user_id",
                    "user_message",
                    "bot_response",
                )
            },
        ),
        (
            "Classification",
            {
                "fields": (
                    "intent_category",
                    "confidence_score",
                    "tokens_used",
                )
            },
        ),
        (
            "Feedback",
            {
                "fields": (
                    "thumbs_up",
                    "slack_reply_ts",
                )
            },
        ),
    )
    list_display = (
        "channel_id",
        "user_id",
        "short_message",
        "intent_category",
        "thumbs_up",
        "tokens_used",
        "nest_created_at",
    )
    list_filter = (
        "thumbs_up",
        "intent_category",
    )
    readonly_fields = (
        "channel_id",
        "user_id",
        "user_message",
        "bot_response",
        "slack_reply_ts",
        "tokens_used",
        "nest_created_at",
        "nest_updated_at",
    )
    search_fields = (
        "channel_id",
        "user_id",
        "user_message",
        "intent_category",
    )

    MESSAGE_TRUNCATE_LENGTH = 60

    @admin.display(description="Message")
    def short_message(self, obj):
        """Return truncated user message for list display."""
        if not obj.user_message:
            return ""
        return (
            obj.user_message[: self.MESSAGE_TRUNCATE_LENGTH] + "…"
            if len(obj.user_message) > self.MESSAGE_TRUNCATE_LENGTH
            else obj.user_message
        )


admin.site.register(BotInteraction, BotInteractionAdmin)
