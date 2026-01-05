"""Mentorship app Module model admin."""

from django.contrib import admin

from apps.mentorship.models.mentor_module import MentorModule
from apps.mentorship.models.module import Module


class MentorModuleInline(admin.TabularInline):
    """Inline admin for MentorModule through model."""

    model = MentorModule
    extra = 1
    fields = ("mentor",)
    autocomplete_fields = ("mentor",)


class ModuleAdmin(admin.ModelAdmin):
    """Admin view for Module model."""

    autocomplete_fields = ("issues",)

    list_display = (
        "name",
        "program",
        "project",
    )

    search_fields = (
        "name",
        "project__name",
    )

    inlines = (MentorModuleInline,)


admin.site.register(Module, ModuleAdmin)
