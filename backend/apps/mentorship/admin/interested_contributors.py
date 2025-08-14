"""Mentorship app interested contributors admin."""

from django.contrib import admin

from apps.mentorship.models import ParticipantInterest


class ParticipantInterestAdmin(admin.ModelAdmin):
    """ParticipantInterest admin."""

    list_display = ("program", "issue", "users_count")
    search_fields = ("program__name", "users__login", "issue__title")
    list_filter = ("program", "issue")

    def users_count(self, obj):
        """Return the count of users interested in the issue."""
        return obj.users.count()

    users_count.short_description = "Users interested"


admin.site.register(ParticipantInterest, ParticipantInterestAdmin)
