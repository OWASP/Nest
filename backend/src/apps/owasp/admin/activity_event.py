"""OWASP app ActivityEvent model admin."""

from django.contrib import admin

from apps.owasp.models.activity_event import ActivityEvent


class ActivityEventAdmin(admin.ModelAdmin):
    """Admin for ActivityEvent model."""

    autocomplete_fields = (
        "github_user",
        "github_repository",
    )
    list_display = (
        "activity_type",
        "github_user",
        "occurred_at",
        "github_repository",
    )
    list_filter = (
        "activity_type",
        "occurred_at",
    )
    search_fields = (
        "activity_type",
        "github_user__login",
        "github_repository__name",
    )


admin.site.register(ActivityEvent, ActivityEventAdmin)
