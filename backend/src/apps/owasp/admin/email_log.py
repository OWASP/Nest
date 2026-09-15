"""Admin registration for EmailLog model."""

from django.contrib import admin

from apps.owasp.models.email_log import EmailLog


class EmailLogAdmin(admin.ModelAdmin):
    """Admin for EmailLog model."""

    list_display = ("get_user", "snapshot", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("snapshot_subscription__user__email",)
    readonly_fields = (
        "snapshot_subscription",
        "snapshot",
        "status",
        "error_message",
        "created_at",
    )

    def has_add_permission(self, request):
        """Prevent manual creation of email logs."""
        return False

    @admin.display(description="User")
    def get_user(self, obj):
        """Return the user from the subscription."""
        return obj.snapshot_subscription.user if obj.snapshot_subscription else "—"


admin.site.register(EmailLog, EmailLogAdmin)
