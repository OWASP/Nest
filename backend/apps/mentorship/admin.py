"""Mentorship app admin."""

from django.contrib import admin

from apps.mentorship.models.mentee import Mentee
from apps.mentorship.models.mentee_program import MenteeProgram
from apps.mentorship.models.mentor import Mentor
from apps.mentorship.models.module import Module
from apps.mentorship.models.program import Program


class MenteeProgramAdmin(admin.ModelAdmin):
    """Admin view for MenteeProgram model."""

    list_display = (
        "mentee",
        "program",
        "experience_level",
    )
    list_filter = ("experience_level", "program")
    search_fields = ("mentee__user__login", "program__name")


class MenteeAdmin(admin.ModelAdmin):
    """Admin view for Mentee model."""

    list_display = (
        "id",
        "github_user",
    )

    search_fields = ("user__name",)


class MentorAdmin(admin.ModelAdmin):
    """Admin view for Mentor model."""

    list_display = (
        "id",
        "github_user",
    )

    search_fields = (
        "user__name",
        "domains",
    )


class ModuleAdmin(admin.ModelAdmin):
    """Admin view for Module model."""

    list_display = (
        "name",
        "project",
    )

    search_fields = (
        "name",
        "project__name",
    )


class ProgramAdmin(admin.ModelAdmin):
    """Admin view for Program model."""

    list_display = (
        "id",
        "name",
        "status",
        "started_at",
        "ended_at",
    )

    search_fields = (
        "name",
        "description",
    )

    list_filter = (
        "status",
        "started_at",
        "ended_at",
    )

    filter_horizontal = ("admins",)


class ProgramModuleAdmin(admin.ModelAdmin):
    """Admin view for ProgramModule model."""

    list_display = (
        "program",
        "module",
        "start_date",
        "end_date",
    )
    search_fields = (
        "program__name",
        "module__name",
    )
    list_filter = ("program",)


admin.site.register(MenteeProgram, MenteeProgramAdmin)
admin.site.register(Mentee, MenteeAdmin)
admin.site.register(Mentor, MentorAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Program, ProgramAdmin)
