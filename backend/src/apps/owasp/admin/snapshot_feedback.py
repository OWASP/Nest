"""Snapshot feedback admin configuration."""

from django.contrib import admin

from apps.owasp.models.snapshot_feedback import SnapshotFeedback


class SnapshotFeedbackAdmin(admin.ModelAdmin):
    """Admin for SnapshotFeedback model."""

    list_display = (
        "snapshot",
        "user",
        "rating",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "rating",
        "created_at",
    )
    ordering = ("-created_at",)
    raw_id_fields = ("snapshot", "user")
    readonly_fields = ("created_at", "updated_at")
    search_fields = (
        "snapshot__key",
        "snapshot__title",
        "user__email",
        "user__username",
        "comment",
    )


admin.site.register(SnapshotFeedback, SnapshotFeedbackAdmin)
