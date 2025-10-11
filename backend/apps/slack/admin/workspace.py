"""Workspace admin configuration."""

from django.contrib import admin

from apps.slack.models.workspace import Workspace


class WorkspaceAdmin(admin.ModelAdmin):
    """Admin for Workspace model."""

    search_fields = (
        "name",
        "slack_workspace_id",
    )


admin.site.register(Workspace, WorkspaceAdmin)
