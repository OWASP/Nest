"""Slack app admin."""

from django.contrib import admin, messages

from apps.slack.models.channel import Channel
from apps.slack.models.event import Event
from apps.slack.models.member import Member
from apps.slack.models.workspace import Workspace


class EventAdmin(admin.ModelAdmin):
    search_fields = (
        "channel_id",
        "channel_name",
        "text",
        "user_id",
        "user_name",
    )
    list_filter = ("trigger",)


class ChannelAdmin(admin.ModelAdmin):
    search_fields = (
        "slack_channel_id",
        "name",
    )
    list_filter = ("is_private",)


class MemberAdmin(admin.ModelAdmin):
    search_fields = ("slack_user_id", "username", "real_name", "email", "user")
    filter_horizontal = ("suggested_users",)
    actions = ["approve_suggested_users"]

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
    search_fields = ("slack_workspace_id", "name")


admin.site.register(Event, EventAdmin)
admin.site.register(Workspace, WorkspaceAdmin)
admin.site.register(Channel, ChannelAdmin)
admin.site.register(Member, MemberAdmin)
