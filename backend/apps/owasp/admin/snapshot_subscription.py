"""Admin registration for SnapshotSubscription model."""

from django.contrib import admin

from apps.owasp.models.project_subscription_preference import ProjectSubscriptionPreference
from apps.owasp.models.snapshot_subscription import SnapshotSubscription


class ProjectSubscriptionPreferenceInline(admin.StackedInline):
    """Inline admin for per-project subscription preferences."""

    model = ProjectSubscriptionPreference
    extra = 0
    can_delete = True
    autocomplete_fields = ("project",)


class SnapshotSubscriptionAdmin(admin.ModelAdmin):
    """Admin for SnapshotSubscription model."""

    list_display = ("user", "frequency", "is_active", "created_at", "updated_at")
    list_filter = ("frequency", "is_active", "created_at")
    search_fields = ("user__email", "user__username")
    raw_id_fields = ("user",)
    readonly_fields = ("unsubscribe_token", "created_at", "updated_at")
    autocomplete_fields = ("chapters",)
    inlines = [ProjectSubscriptionPreferenceInline]

    fieldsets = (
        (None, {"fields": ("user", "frequency", "is_active")}),
        (
            "System",
            {
                "fields": ("unsubscribe_token", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
        (
            "General Subscriptions",
            {
                "fields": (
                    "include_chapters",
                    "include_events",
                    "include_posts",
                    "include_users",
                ),
            },
        ),
        (
            "Chapter Subscriptions",
            {
                "fields": ("chapters",),
            },
        ),
    )


admin.site.register(SnapshotSubscription, SnapshotSubscriptionAdmin)
