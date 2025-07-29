"""Slack app admin."""

from django.contrib import admin, messages
from django.http import HttpRequest

from apps.slack.models import (
    Conversation,
    Event,
    Member,
    Message,
    Workspace,
)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
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
        ("Conversation Information", {
            "fields": ("slack_channel_id", "name", "created_at", "slack_creator_id")
        }),
        ("Properties", {
            "fields": ("is_private", "is_archived", "is_general")
        }),
        ("Content", {
            "fields": ("topic", "purpose")
        }),
        ("Additional Attributes", {
            "fields": ("sync_messages",)
        }),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin for Event model."""

    list_display = ("nest_created_at", "trigger", "user_id")
    list_filter = ("trigger",)
    search_fields = (
        "channel_id",
        "channel_name",
        "text",
        "user_id",
        "user_name",
    )


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    """Admin for Member model."""

    actions = ("approve_suggested_users",)
    autocomplete_fields = ("user",)
    filter_horizontal = ("suggested_users",)
    list_filter = ("is_bot", "workspace")
    search_fields = (
        "slack_user_id",
        "username",
        "real_name",
        "email",
        "user__login",
    )

    @admin.action(description="Approve the suggested user (if only one exists)")
    def approve_suggested_users(self, request: HttpRequest, queryset):
        """Approve all suggested users for selected members, enforcing one-to-one constraints."""
        for entity in queryset:
            suggestions = entity.suggested_users.all()
            count = suggestions.count()

            if count == 1:
                entity.user = suggestions.first()
                entity.save()
                self.message_user(
                    request,
                    f"Assigned user for {entity}.",
                    messages.SUCCESS,
                )
            elif count > 1:
                self.message_user(
                    request,
                    f"Error: Multiple suggested users found for {entity}. "
                    "Only one user can be assigned due to the one-to-one constraint.",
                    messages.ERROR,
                )
            else:
                self.message_user(
                    request,
                    f"No suggested users found for {entity}.",
                    messages.WARNING,
                )


@admin.register(Message)
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
    list_filter = ("has_replies", "conversation")
    search_fields = (
        "slack_message_id",
        "raw_data__text",
    )


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    """Admin for Workspace model."""

    search_fields = (
        "name",
        "slack_workspace_id",
    )
