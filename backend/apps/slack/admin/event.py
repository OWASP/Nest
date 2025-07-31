"""Event admin configuration."""

from django.contrib import admin

from apps.slack.models.event import Event

from .mixins import EventAdminMixin


class EventAdmin(EventAdminMixin, admin.ModelAdmin):
    """Admin for Event model."""

    list_display = ("nest_created_at", "trigger", "user_id")
    list_filter = ("trigger",)
    ordering = ("-nest_created_at",)
    search_fields = ("channel_id", "channel_name", "text", "user_id", "user_name")


admin.site.register(Event, EventAdmin)
