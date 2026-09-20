"""Workspace admin configuration."""

from django.contrib import admin

from apps.slack.models.workspace import Workspace


class WorkspaceAdmin(admin.ModelAdmin):
    """Admin for Workspace model."""

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "slack_workspace_id",
                    "total_members_count",
                )
            },
        ),
        (
            "Content reporting",
            {
                "fields": (
                    "content_report_alert_channel_id",
                    "content_report_alert_user_ids",
                )
            },
        ),
        (
            "Invite link alerts",
            {
                "fields": (
                    "invite_link_alert_channel_id",
                    "invite_link_alert_user_ids",
                    "invite_link_alert_member_offset",
                    "invite_link_created_at",
                    "invite_link_commit_sha",
                    "invite_link_member_count",
                    "invite_link_last_alert_sent_at",
                    "invite_link_last_alert_message_ts",
                )
            },
        ),
    )
    search_fields = (
        "name",
        "slack_workspace_id",
    )


admin.site.register(Workspace, WorkspaceAdmin)
