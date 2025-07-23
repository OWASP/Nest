"""Mentorship app admin."""

from django.contrib import admin

from apps.mentorship.models.mentee import Mentee
from apps.mentorship.models.mentee_program import MenteeProgram
from apps.mentorship.models.mentor import Mentor
from apps.mentorship.models.module import Module
from apps.mentorship.models.program import Program
from apps.mentorship.models.task import Task
from apps.mentorship.models.task_level import TaskLevel


class MenteeAdmin(admin.ModelAdmin):
    """Admin view for Mentee model."""

    list_display = ("github_user",)

    search_fields = (
        "github_user__login",
        "github_user__name",
    )


class MenteeProgramAdmin(admin.ModelAdmin):
    """Admin view for MenteeProgram model."""

    list_display = (
        "mentee",
        "program",
        "experience_level",
    )
    list_filter = (
        "experience_level",
        "program",
    )
    search_fields = (
        "mentee__github_user__login",
        "mentee__github_user__name",
        "program__name",
    )


class MentorAdmin(admin.ModelAdmin):
    """Admin view for Mentor model."""

    list_display = ("github_user",)

    search_fields = (
        "github_user__login",
        "github_user__name",
        "domains",
    )


class ModuleAdmin(admin.ModelAdmin):
    """Admin view for Module model."""

    list_display = (
        "name",
        "program",
        "project",
    )

    search_fields = (
        "name",
        "project__name",
    )


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


class TaskAdmin(admin.ModelAdmin):
    """Admin view for Task model."""

    list_display = (
        "issue",
        "assignee",
        "module",
        "status",
        "assigned_at",
        "deadline_at",
    )

    search_fields = (
        "issue__title",
        "assignee__github_user__login",
        "module__name",
    )

    list_filter = ("status", "module", "assignee")


class TaskLevelAdmin(admin.ModelAdmin):
    """Admin view for TaskLevel model."""

    list_display = (
        "description",
        "labels",
        "module",
        "name",
    )

    search_fields = (
        "name",
        "module__name",
    )


admin.site.register(MenteeProgram, MenteeProgramAdmin)
admin.site.register(Mentee, MenteeAdmin)
admin.site.register(Mentor, MentorAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskLevel, TaskLevelAdmin)
