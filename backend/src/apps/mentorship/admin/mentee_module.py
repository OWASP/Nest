"""Mentorship app MenteeModule model admin."""

from django.contrib import admin

from apps.mentorship.models.mentee_module import MenteeModule


@admin.register(MenteeModule)
class MenteeModuleAdmin(admin.ModelAdmin):
    """Admin view for MenteeModule model."""

    autocomplete_fields = (
        "mentee",
        "module",
    )

    list_display = (
        "mentee",
        "module",
        "started_at",
        "ended_at",
    )

    list_filter = (
        "module__program",
        "started_at",
        "ended_at",
    )

    ordering = (
        "mentee__github_user__login",
        "module__name",
    )

    search_fields = (
        "mentee__github_user__login",
        "mentee__github_user__name",
        "module__name",
        "module__program__name",
    )
