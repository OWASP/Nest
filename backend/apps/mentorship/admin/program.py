"""Mentorship app Program model admin."""

from django.contrib import admin

from apps.mentorship.models import Program


class ProgramAdmin(admin.ModelAdmin):
    """Admin view for Program model."""

    list_display = (
        "name",
        "status",
        "started_at",
        "ended_at",
    )

    search_fields = (
        "name",
        "description",
    )

    list_filter = ("status",)

    filter_horizontal = ("admins",)


admin.site.register(Program, ProgramAdmin)
