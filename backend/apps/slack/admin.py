"""Slack app admin."""

from django.contrib import admin, messages

from apps.slack.models.conversation import Conversation
from apps.slack.models.event import Event
from apps.slack.models.member import Member
from apps.slack.models.workspace import Workspace


class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slack_channel_id",
        "created_at",
        "is_private",
        "is_archived",
        "is_general",
    )
    search_fields = (
        "name",
        "topic",
        "purpose",
        "slack_channel_id",
        "slack_creator_id",
    )
    list_filter = (
        "created_at",
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


class MemberAdmin(admin.ModelAdmin):
    actions = ("approve_suggested_users",)
    autocomplete_fields = ("user",)
    filter_horizontal = ("suggested_users",)
    search_fields = (
        "slack_user_id",
        "username",
        "real_name",
        "email",
        "user",
    )

    def approve_suggested_users(self, request, queryset):
        """Approve all suggested users for selected members, enforcing one-to-one constraints."""
        for entity in queryset:
            suggestions = entity.suggested_users.all()

            if suggestions.count() == 1:
                entity.user = suggestions.first()  # only one suggested user
                entity.save()
                self.message_user(
                    request,
                    f" assigned user for {entity}.",
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


class WorkspaceAdmin(admin.ModelAdmin):
    search_fields = (
        "name",
        "slack_workspace_id",
    )


admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Workspace, WorkspaceAdmin)
