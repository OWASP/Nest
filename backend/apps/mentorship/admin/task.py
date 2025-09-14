"""Mentorship app Task model admin."""

from django.contrib import admin

from apps.mentorship.models.task import Task


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

    list_filter = ("status", "module")

    ordering = ["-assigned_at"]


admin.site.register(Task, TaskAdmin)
