"""Mentorship app Mentee model admin."""

from django.contrib import admin

from apps.mentorship.models.mentee import Mentee


class MenteeAdmin(admin.ModelAdmin):
    """Admin view for Mentee model."""

    autocomplete_fields = (
        "github_user",
        "nest_user",
    )

    list_display = ("github_user",)

    search_fields = (
        "github_user__login",
        "github_user__name",
    )


admin.site.register(Mentee, MenteeAdmin)
