"""Mentorship app Module model admin."""

from django.contrib import admin

from apps.mentorship.models.module import Module


class ModuleAdmin(admin.ModelAdmin):
    """Admin view for Module model."""

    list_display = (
        "name",
        "program",
        "project",
        "linked_issue_labels",
    )
    filter_horizontal = ("linked_issues",)

    search_fields = (
        "name",
        "project__name",
    )


admin.site.register(Module, ModuleAdmin)
