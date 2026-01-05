"""Mentorship app Program model admin."""

from django.contrib import admin

from apps.mentorship.models import Program
from apps.mentorship.models.program_admin import ProgramAdmin as ProgramAdminThroughModel


class ProgramAdminInline(admin.TabularInline):
    """Inline admin for ProgramAdmin through model."""

    model = ProgramAdminThroughModel
    extra = 1
    autocomplete_fields = ("user",)


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

    inlines = (ProgramAdminInline,)


admin.site.register(Program, ProgramAdmin)
