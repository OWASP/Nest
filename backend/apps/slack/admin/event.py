"""Event admin configuration."""

from django.contrib import admin

from apps.slack.models.event import Event

from .mixins import SlackChannelRelatedAdminMixin, SlackEntityAdminMixin


class EventAdmin(admin.ModelAdmin, SlackEntityAdminMixin, SlackChannelRelatedAdminMixin):
    """Admin for Event model."""

    list_display = (
        "nest_created_at",
        "trigger",
        "user_id",
    )
    list_filter = ("trigger",)
    search_fields = SlackChannelRelatedAdminMixin.base_slack_search_fields + (
        "text",
        "user_id",
        "user_name",
    )


admin.site.register(Event, EventAdmin)
