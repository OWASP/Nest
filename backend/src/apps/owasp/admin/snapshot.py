"""Snapshot admin configuration."""

from django.contrib import admin

from apps.owasp.models.snapshot import Snapshot

from .mixins import StandardOwaspAdminMixin


class SnapshotAdmin(admin.ModelAdmin, StandardOwaspAdminMixin):
    """Admin for Snapshot model."""

    autocomplete_fields = (
        "new_chapters",
        "new_issues",
        "new_projects",
        "new_releases",
        "new_users",
    )
    list_display = (
        "title",
        "start_at",
        "end_at",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "status",
        "start_at",
        "end_at",
    )
    ordering = ("-start_at",)
    search_fields = (
        "title",
        "key",
        "status",
        "error_message",
    )


admin.site.register(Snapshot, SnapshotAdmin)
