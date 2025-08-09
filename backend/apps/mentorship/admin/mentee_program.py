"""Mentorship app MenteeProgram model admin."""

from django.contrib import admin

from apps.mentorship.models.mentee_program import MenteeProgram


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


admin.site.register(MenteeProgram, MenteeProgramAdmin)
