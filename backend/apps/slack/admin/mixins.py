"""Slack admin mixins for common functionality."""

from django.contrib import messages


class BaseSlackAdminMixin:
    """Base mixin for Slack admin classes providing common patterns."""

    # Common readonly fields for Slack entities
    base_readonly_fields: tuple[str, ...] = ()
    base_list_display: tuple[str, ...] = ()
    base_list_filter: tuple[str, ...] = ()
    base_slack_search_fields: tuple[str, ...] = ()
    base_autocomplete_fields: tuple[str, ...] = ()
    base_list_select_related: tuple[str, ...] = ()
    base_ordering: tuple[str, ...] = ("-created_at",)

    def get_readonly_fields(self, request, obj=None):
        """Get readonly fields with common Slack fields."""
        return super().get_readonly_fields(request, obj) + self.base_readonly_fields


class SlackEntityAdminMixin(BaseSlackAdminMixin):
    """Mixin for Slack entities with common patterns."""

    base_readonly_fields: tuple[str, ...] = ("created_at",)

    def get_list_display(self, request):
        """Get list display with created_at if available."""
        display = list(super().get_list_display(request))
        if hasattr(self.model, "created_at") and "created_at" not in display:
            display.append("created_at")
        return tuple(display)


class SlackChannelRelatedAdminMixin(BaseSlackAdminMixin):
    """Mixin for Slack admin classes dealing with channel-related data."""

    base_slack_search_fields: tuple[str, ...] = (
        "channel_id",
        "channel_name",
        "slack_channel_id",
    )

    base_readonly_fields: tuple[str, ...] = ("slack_channel_id", "slack_creator_id")

    base_channel_filters: tuple[str, ...] = (
        "is_archived",
        "is_channel",
        "is_general",
        "is_im",
        "is_private",
    )


class SlackUserRelatedAdminMixin(BaseSlackAdminMixin):
    """Mixin for Slack admin classes dealing with user-related data."""

    base_autocomplete_fields: tuple[str, ...] = ("user",)
    base_list_display: tuple[str, ...] = (
        "slack_user_id",
        "username",
        "real_name",
        "is_bot",
        "workspace",
    )
    base_list_filter: tuple[str, ...] = ("is_bot", "workspace")
    base_list_select_related: tuple[str, ...] = ("user", "workspace")
    base_ordering: tuple[str, ...] = ("-created_at",)
    base_slack_search_fields: tuple[str, ...] = (
        "slack_user_id",
        "username",
        "real_name",
        "email",
        "user__login",
    )


class SlackMessageRelatedAdminMixin(BaseSlackAdminMixin):
    """Mixin for Slack admin classes dealing with message-related data."""

    base_autocomplete_fields: tuple[str, ...] = ("author", "conversation")
    base_list_display: tuple[str, ...] = ("created_at",)
    base_slack_search_fields: tuple[str, ...] = (
        "slack_message_id",
        "text",
        "raw_data__text",
    )


class SlackWorkspaceRelatedAdminMixin(BaseSlackAdminMixin):
    """Mixin for Slack admin classes dealing with workspace-related data."""

    base_list_display: tuple[str, ...] = ("name", "slack_workspace_id", "created_at")
    base_ordering: tuple[str, ...] = ("-created_at",)
    base_slack_search_fields: tuple[str, ...] = (
        "name",
        "slack_workspace_id",
    )


class SuggestedUsersAdminMixin:
    """Mixin for admin classes that handle suggested users approval."""

    actions: tuple[str, ...] = ("approve_suggested_users",)
    filter_horizontal: tuple[str, ...] = ("suggested_users",)

    def approve_suggested_users(self, request, queryset):
        """Approve all suggested users for selected members, enforcing one-to-one constraints."""
        for entity in queryset:
            suggestions = entity.suggested_users.all()

            if suggestions.count() == 1:
                entity.user = suggestions.first()  # only one suggested user
                entity.save()
                self.message_user(
                    request,
                    f"Assigned user for {entity}.",
                    messages.SUCCESS,
                )
            elif suggestions.count() > 1:
                self.message_user(
                    request,
                    f"Error: Multiple suggested users found for {entity}. "
                    f"Only one user can be assigned due to the one-to-one constraint.",
                    messages.ERROR,
                )
            else:
                self.message_user(
                    request,
                    f"No suggested users found for {entity}.",
                    messages.WARNING,
                )

    approve_suggested_users.short_description = "Approve the suggested user (if only one exists)"


class ConversationAdminMixin(SlackChannelRelatedAdminMixin):
    """Specific mixin for Conversation admin with common conversation patterns."""

    base_autocomplete_fields: tuple[str, ...] = ()
    base_list_display: tuple[str, ...] = ("name", "slack_channel_id", "created_at")
    base_list_filter: tuple[str, ...] = (
        "sync_messages",
        *SlackChannelRelatedAdminMixin.base_channel_filters,
    )
    base_list_select_related: tuple[str, ...] = ("workspace",)
    base_ordering: tuple[str, ...] = ("-created_at",)
    base_readonly_fields: tuple[str, ...] = ("slack_channel_id", "created_at", "slack_creator_id")
    base_slack_search_fields: tuple[str, ...] = (
        *SlackChannelRelatedAdminMixin.base_slack_search_fields,
        "name",
        "topic",
        "purpose",
        "slack_creator_id",
    )

    def get_fieldsets(self, _request, _obj=None):
        """Get standard fieldsets for conversation."""
        return (
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


class MessageAdminMixin(SlackMessageRelatedAdminMixin):
    """Specific mixin for Message admin with common message patterns."""

    base_autocomplete_fields: tuple[str, ...] = ("author", "conversation", "parent_message")
    base_list_display: tuple[str, ...] = ("created_at", "has_replies", "author", "conversation")
    base_list_filter: tuple[str, ...] = ("has_replies", "conversation")
    base_list_select_related: tuple[str, ...] = ("author", "conversation", "parent_message")
    base_ordering: tuple[str, ...] = ("-created_at",)


class EventAdminMixin(BaseSlackAdminMixin):
    """Specific mixin for Event admin with common event patterns."""

    base_list_display: tuple[str, ...] = ("nest_created_at", "trigger", "user_id")
    base_list_filter: tuple[str, ...] = ("trigger",)
    base_ordering: tuple[str, ...] = ("-nest_created_at",)
    base_slack_search_fields: tuple[str, ...] = (
        "channel_id",
        "channel_name",
        "text",
        "user_id",
        "user_name",
    )
