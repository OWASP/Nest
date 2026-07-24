"""Admin registration for SnapshotSubscription model."""

from django.contrib import admin

from apps.owasp.models.snapshot_subscription import SnapshotSubscription


class SnapshotSubscriptionAdmin(admin.ModelAdmin):
    """Admin for SnapshotSubscription model."""

    list_display = ("user", "frequency", "is_active", "created_at", "updated_at")
    list_filter = ("frequency", "is_active", "created_at")
    search_fields = ("user__email", "user__username")
    raw_id_fields = ("user",)
    readonly_fields = ("unsubscribe_token", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("user", "frequency", "is_active")}),
        (
            "Content Toggles",
            {
                "fields": (
                    "include_chapters",
                    "include_events",
                    "include_issues",
                    "include_posts",
                    "include_projects",
                    "include_pull_requests",
                    "include_releases",
                    "include_users",
                ),
            },
        ),
        (
            "System",
            {
                "fields": ("unsubscribe_token", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


admin.site.register(SnapshotSubscription, SnapshotSubscriptionAdmin)
