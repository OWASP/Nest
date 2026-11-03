"""Event admin configuration."""

from django.contrib import admin

from apps.owasp.models.event import Event

from .mixins import StandardOwaspAdminMixin


class EventAdmin(admin.ModelAdmin, StandardOwaspAdminMixin):
    """Admin for Event model."""

    list_display = (
        "name",
        "suggested_location",
    )
    search_fields = ("name",)


admin.site.register(Event, EventAdmin)
