"""Django admin screen for emitted Slack content reports."""

from django.contrib import admin

from apps.slack.models.content_report import ContentReport


@admin.register(ContentReport)
class ContentReportAdmin(admin.ModelAdmin):
    """Admin list/search controls for emitted content reports."""

    list_display = (
        "conversation",
        "message_ts",
        "report_type",
        "source",
        "reaction_count",
        "nest_created_at",
    )
    list_filter = ("source", "report_type")
    readonly_fields = (
        "conversation",
        "message",
        "message_ts",
        "report_type",
        "source",
        "reaction_count",
        "reporter_user_ids",
        "alert_message_ts",
    )
    search_fields = (
        "conversation__name",
        "message_ts",
        "report_type",
        "source",
    )

    def has_add_permission(self, request):
        """Disable manual content report creation in Django admin."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable manual content report deletion in Django admin."""
        return False
