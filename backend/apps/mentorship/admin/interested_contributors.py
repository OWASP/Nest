"""Mentorship app interested contributors admin."""

from django.contrib import admin

from apps.mentorship.models import ParticipantInterest


class ParticipantInterestAdmin(admin.ModelAdmin):
    """ParticipantInterest admin."""

    list_display = (
        "program",
        "user",
        "issue",
    )

    search_fields = (
        "program__name",
        "user__username",
        "issue__title",
    )


admin.site.register(ParticipantInterest, ParticipantInterestAdmin)
