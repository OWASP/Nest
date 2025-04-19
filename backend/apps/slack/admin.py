"""Slack app admin."""

from django.contrib import admin

from apps.slack.models.conversation import Conversation
from apps.slack.models.event import Event


class ConversationAdmin(admin.ModelAdmin):
    """Admin configuration for Conversation model."""

    list_display = (
        "name",
        "entity_id",
        "created_at",
        "is_private",
        "is_archived",
        "is_general",
    )
    search_fields = (
        "name",
        "topic",
        "purpose",
        "entity_id",
        "creator_id",
    )
    list_filter = (
        "created_at",
        "is_private",
        "is_archived",
        "is_general",
    )
    readonly_fields = (
        "entity_id",
        "created_at",
        "creator_id",
    )
    fieldsets = (
        (
            "Conversation Information",
            {
                "fields": (
                    "entity_id",
                    "name",
                    "created_at",
                    "creator_id",
                )
            },
        ),
        (
            "Properties",
            {
                "fields": (
                    "is_private",
                    "is_archived",
                    "is_general",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "topic",
                    "purpose",
                )
            },
        ),
    )


class EventAdmin(admin.ModelAdmin):
    search_fields = (
        "channel_id",
        "channel_name",
        "text",
        "user_id",
        "user_name",
    )
    list_filter = ("trigger",)


admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Event, EventAdmin)
