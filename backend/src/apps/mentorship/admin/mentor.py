"""Mentorship app Mentor model admin."""

from django.contrib import admin

from apps.mentorship.models.mentor import Mentor


class MentorAdmin(admin.ModelAdmin):
    """Admin view for Mentor model."""

    list_display = ("github_user",)

    search_fields = (
        "github_user__login",
        "github_user__name",
        "domains",
    )


admin.site.register(Mentor, MentorAdmin)
