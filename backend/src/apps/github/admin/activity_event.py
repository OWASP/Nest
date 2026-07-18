"""GitHub app ActivityEvent model admin."""

from django.contrib import admin

from apps.github.models.activity_event import ActivityEvent


class ActivityEventAdmin(admin.ModelAdmin):
    """Admin for ActivityEvent model."""

    autocomplete_fields = (
        "actor",
        "repository",
    )
    list_display = (
        "activity_type",
        "actor",
        "nest_created_at",
        "occurred_at",
        "repository",
    )
    list_filter = (
        "activity_type",
        "occurred_at",
    )
    search_fields = (
        "activity_type",
        "actor__login",
        "repository__name",
    )


admin.site.register(ActivityEvent, ActivityEventAdmin)
