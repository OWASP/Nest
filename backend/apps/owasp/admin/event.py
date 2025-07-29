from django.contrib import admin

from apps.owasp.models.event import Event


class EventAdmin(admin.ModelAdmin):
    """Admin for Event model."""

    list_display = (
        "name",
        "suggested_location",
    )
    search_fields = ("name",)


admin.site.register(Event, EventAdmin)
