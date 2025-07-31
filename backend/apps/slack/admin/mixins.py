"""Slack admin mixins for common functionality."""

from django.contrib import admin, messages


class BaseSlackAdminMixin:
    """Base mixin for Slack admin classes providing common patterns."""

    # Common Slack ID search patterns
    base_slack_search_fields = ()

    def get_slack_search_fields(self, *additional_fields):
        """Get Slack-specific search fields with additional fields."""
        return self.base_slack_search_fields + additional_fields


class SlackEntityAdminMixin(BaseSlackAdminMixin):
    """Mixin for Slack entities with common Slack ID patterns."""

    def get_common_slack_list_display(self, *additional_fields):
        """Get common list display fields for Slack entities."""
        base_fields = ("created_at",) if hasattr(self.model, "created_at") else ()
        return additional_fields + base_fields


class SlackUserRelatedAdminMixin(BaseSlackAdminMixin):
    """Mixin for Slack admin classes dealing with user-related data."""

    base_slack_search_fields = (
        "slack_user_id",
        "username",
        "real_name",
        "email",
    )


class SlackChannelRelatedAdminMixin(BaseSlackAdminMixin):
    """Mixin for Slack admin classes dealing with channel-related data."""

    base_slack_search_fields = (
        "channel_id",
        "channel_name",
        "slack_channel_id",
    )


class SlackMessageRelatedAdminMixin(BaseSlackAdminMixin):
    """Mixin for Slack admin classes dealing with message-related data."""

    base_slack_search_fields = (
        "slack_message_id",
        "text",
        "raw_data__text",
    )


class SlackWorkspaceRelatedAdminMixin(BaseSlackAdminMixin):
    """Mixin for Slack admin classes dealing with workspace-related data."""

    base_slack_search_fields = (
        "name",
        "slack_workspace_id",
    )


class SuggestedUsersAdminMixin:
    """Mixin for admin classes that handle suggested users approval."""

    actions = ("approve_suggested_users",)
    filter_horizontal = ("suggested_users",)

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
