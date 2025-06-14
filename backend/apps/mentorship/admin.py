"""Mentorship app admin."""

from django.contrib import admin

from apps.mentorship.models.mentee import Mentee
from apps.mentorship.models.mentor import Mentor
from apps.mentorship.models.module import Module
from apps.mentorship.models.program import Program


class MenteeAdmin(admin.ModelAdmin):
    """Admin view for Mentee model."""

    list_display = (
        "id",
        "user",
        "level",
        "issues_worked_on",
        "prs_opened",
        "prs_merged",
    )

    search_fields = ("user__name",)

    list_filter = ("level",)


class MentorAdmin(admin.ModelAdmin):
    """Admin view for Mentor model."""

    list_display = (
        "id",
        "user",
        "years_of_experience",
        "mentee_limit",
        "active_mentees",
        "is_available",
    )

    search_fields = (
        "user__name",
        "domain",
    )


class ModuleAdmin(admin.ModelAdmin):
    """Admin view for Module model."""

    list_display = (
        "name",
        "project",
        "start_date",
        "end_date",
    )

    search_fields = (
        "name",
        "project__name",
    )

    filter_horizontal = ("mentors", "mentees")


class ProgramAdmin(admin.ModelAdmin):
    """Admin view for Program model."""

    list_display = (
        "id",
        "name",
        "status",
        "start_date",
        "end_date",
    )

    search_fields = (
        "name",
        "description",
    )

    list_filter = (
        "status",
        "start_date",
        "end_date",
    )

    filter_horizontal = ("owners", "modules")


admin.site.register(Mentee, MenteeAdmin)
admin.site.register(Mentor, MentorAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Program, ProgramAdmin)
