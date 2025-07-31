"""Workspace admin configuration."""

from django.contrib import admin

from apps.slack.models.workspace import Workspace

from .mixins import SlackWorkspaceRelatedAdminMixin


class WorkspaceAdmin(SlackWorkspaceRelatedAdminMixin, admin.ModelAdmin):
    """Admin for Workspace model."""

    list_display = ("name", "slack_workspace_id", "created_at")
    ordering = ("-created_at",)
    search_fields = ("name", "slack_workspace_id")


admin.site.register(Workspace, WorkspaceAdmin)
