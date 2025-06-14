"""Mentorship app admin."""

from django.contrib import admin

from apps.mentorship.models.mentee import Mentee
from apps.mentorship.models.mentor import Mentor


class MenteeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "level",
        "issues_worked_on",
        "prs_opened",
        "prs_merged",
    )

    search_fields = (
        "user__login",
        "user__name",
    )

    list_filter = ("level",)


class MentorAdmin(admin.ModelAdmin):
    search_fields = (
        "user",
        "years_of_experience",
        "domain",
    )


admin.site.register(Mentee, MenteeAdmin)
admin.site.register(Mentor, MentorAdmin)
