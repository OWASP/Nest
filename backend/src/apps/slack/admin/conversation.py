"""Conversation admin configuration."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.slack.models.conversation import Conversation


@admin.action(description="Enable NestBot assistant for selected conversations")
def enable_nestbot_assistant(modeladmin, request, queryset):  # noqa: ARG001
    """Enable is_nest_bot_assistant_enabled for selected conversations."""
    updated = queryset.update(is_nest_bot_assistant_enabled=True)
    modeladmin.message_user(
        request, _(f"NestBot assistant enabled for {updated} conversation(s).")
    )


@admin.action(description="Disable NestBot assistant for selected conversations")
def disable_nestbot_assistant(modeladmin, request, queryset):  # noqa: ARG001
    """Disable is_nest_bot_assistant_enabled for selected conversations."""
    updated = queryset.update(is_nest_bot_assistant_enabled=False)
    modeladmin.message_user(
        request, _(f"NestBot assistant disabled for {updated} conversation(s).")
    )


class ConversationAdmin(admin.ModelAdmin):
    """Admin for Conversation model."""

    actions = [enable_nestbot_assistant, disable_nestbot_assistant]

    fieldsets = (
        (
            "Conversation Information",
            {"fields": ("slack_channel_id", "name", "created_at", "slack_creator_id")},
        ),
        (
            "Properties",
            {
                "fields": (
                    "is_private",
                    "is_archived",
                    "is_general",
                    "is_nest_bot_assistant_enabled",
                )
            },
        ),
        ("Content", {"fields": ("topic", "purpose")}),
        ("Additional attributes", {"fields": ("sync_messages",)}),
    )
    list_display = (
        "name",
        "slack_channel_id",
        "is_nest_bot_assistant_enabled",
        "created_at",
        "total_members_count",
    )
    list_filter = (
        "is_nest_bot_assistant_enabled",
        "sync_messages",
        "is_archived",
        "is_channel",
        "is_general",
        "is_im",
        "is_private",
    )
    readonly_fields = ("slack_channel_id", "created_at", "slack_creator_id")
    search_fields = ("name", "topic", "purpose", "slack_channel_id", "slack_creator_id")


admin.site.register(Conversation, ConversationAdmin)
