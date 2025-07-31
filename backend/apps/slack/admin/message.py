"""Message admin configuration."""

from django.contrib import admin

from apps.slack.models.message import Message

from .mixins import SlackEntityAdminMixin, SlackMessageRelatedAdminMixin


class MessageAdmin(admin.ModelAdmin, SlackEntityAdminMixin, SlackMessageRelatedAdminMixin):
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
    search_fields = SlackMessageRelatedAdminMixin.base_slack_search_fields


admin.site.register(Message, MessageAdmin)
