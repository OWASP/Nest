"""Mentorship app ContributorInterest admin."""

from django.contrib import admin

from apps.mentorship.models import ContributorInterest


class ContributorInterestAdmin(admin.ModelAdmin):
    """ContributorInterest admin."""

    list_display = ("module", "issue", "users_count")
    search_fields = ("module__name", "users__login", "issue__title")
    list_filter = ("module", "issue")

    def users_count(self, obj):
        """Return the count of users interested in the issue."""
        return obj.users.count()

    users_count.short_description = "Interested Users"


admin.site.register(ContributorInterest, ContributorInterestAdmin)
