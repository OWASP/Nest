"""Workspace admin configuration."""

from django.contrib import admin

from apps.slack.models.workspace import Workspace

from .mixins import SlackWorkspaceRelatedAdminMixin


class WorkspaceAdmin(admin.ModelAdmin, SlackWorkspaceRelatedAdminMixin):
    """Admin for Workspace model."""

    search_fields = SlackWorkspaceRelatedAdminMixin.base_slack_search_fields


admin.site.register(Workspace, WorkspaceAdmin)
