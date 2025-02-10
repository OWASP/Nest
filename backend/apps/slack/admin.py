"""Slack app admin."""

from django.contrib import admin

from apps.slack.models.event import Event


class EventAdmin(admin.ModelAdmin):
    search_fields = (
        "channel_id",
        "channel_name",
        "text",
        "user_id",
        "user_name",
    )
    list_filter = ("trigger",)


admin.site.register(Event, EventAdmin)
