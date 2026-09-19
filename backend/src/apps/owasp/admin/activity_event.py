"""OWASP app ActivityEvent model admin."""

from django.contrib import admin
from django.db import models

from apps.owasp.models.activity_event import ActivityEvent


class ActivityEventAdmin(admin.ModelAdmin):
    """Admin for ActivityEvent model."""

    autocomplete_fields = (
        "github_user",
        "github_repository",
    )
    list_display = (
        "activity_type",
        "github_repository",
        "github_user",
        "occurred_at",
    )
    list_filter = (
        "activity_type",
        "occurred_at",
    )
    search_fields = (
        "activity_type",
        "github_repository__name",
        "github_user__login",
    )

    def get_queryset(self, request) -> models.QuerySet:
        """Retrieve optimized queryset with related fields."""
        return (
            super()
            .get_queryset(request)
            .select_related(
                "github_user",
                "github_repository__owner",
            )
        )


admin.site.register(ActivityEvent, ActivityEventAdmin)
