"""Message admin configuration."""

from django.contrib import admin

from apps.slack.models.message import Message


class MessageAdmin(admin.ModelAdmin):
    """Admin for Message model."""

    autocomplete_fields = (
        "author",
        "conversation",
        "parent_message",
    )
    list_display = (
        "created_at",
        "has_replies",
        "author",
        "conversation",
    )
    list_filter = (
        "has_replies",
        "conversation",
    )
    search_fields = (
        "slack_message_id",
        "raw_data__text",
    )


admin.site.register(Message, MessageAdmin)
