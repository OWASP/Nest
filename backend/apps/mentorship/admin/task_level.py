"""Mentorship app TaskLevel model admin."""

from django.contrib import admin

from apps.mentorship.models.task_level import TaskLevel


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


admin.site.register(TaskLevel, TaskLevelAdmin)
