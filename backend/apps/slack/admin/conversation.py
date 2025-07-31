"""Conversation admin configuration."""

from django.contrib import admin

from apps.slack.models.conversation import Conversation

from .mixins import SlackChannelRelatedAdminMixin, SlackEntityAdminMixin


class ConversationAdmin(admin.ModelAdmin, SlackEntityAdminMixin, SlackChannelRelatedAdminMixin):
    """Admin for Conversation model."""

    list_display = (
        "name",
        "slack_channel_id",
        "created_at",
        "total_members_count",
    )
    search_fields = (
        "name",
        "topic",
        "purpose",
        "slack_channel_id",
        "slack_creator_id",
    )
    list_filter = (
        "sync_messages",
        "is_archived",
        "is_channel",
        "is_general",
        "is_im",
        "is_private",
    )
    readonly_fields = (
        "slack_channel_id",
        "created_at",
        "slack_creator_id",
    )
    fieldsets = (
        (
            "Conversation Information",
            {
                "fields": (
                    "slack_channel_id",
                    "name",
                    "created_at",
                    "slack_creator_id",
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
        (
            "Additional attributes",
            {"fields": ("sync_messages",)},
        ),
    )


admin.site.register(Conversation, ConversationAdmin)
