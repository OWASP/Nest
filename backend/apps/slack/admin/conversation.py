"""Conversation admin configuration."""

from django.contrib import admin
from django.db import models

from apps.slack.models.conversation import Conversation

from .mixins import ConversationAdminMixin, SlackChannelRelatedAdminMixin


class ConversationAdmin(ConversationAdminMixin, admin.ModelAdmin):
    """Admin for Conversation model."""

    list_display = ("name", "slack_channel_id", "created_at", "total_members_count")
    list_filter = (
        "sync_messages",
        "is_archived",
        "is_channel",
        "is_general",
        "is_im",
        "is_private",
    )
    list_select_related = ("workspace",)
    ordering = ("-created_at",)
    readonly_fields = ("slack_channel_id", "created_at", "slack_creator_id")
    search_fields = (
        *SlackChannelRelatedAdminMixin.base_slack_search_fields,
        "name",
        "topic",
        "purpose",
        "slack_creator_id",
    )

    def get_queryset(self, request):
        """Optimize queryset to reduce N+1 queries for member count."""
        return (
            super()
            .get_queryset(request)
            .annotate(_members_count=models.Count("members", distinct=True))
        )

    def total_members_count(self, obj):
        """Display optimized member count."""
        return getattr(obj, "_members_count", obj.total_members_count)

    total_members_count.admin_order_field = "_members_count"
    total_members_count.short_description = "Total Members"


admin.site.register(Conversation, ConversationAdmin)
