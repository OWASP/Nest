"""Mentorship app IssueUserInterest admin."""

from django.contrib import admin

from apps.mentorship.models import IssueUserInterest


class IssueUserInterestAdmin(admin.ModelAdmin):
    """IssueUserInterest admin."""

    list_display = (
        "module",
        "issue",
    )

    list_filter = ("module",)

    search_fields = (
        "module__name",
        "user__login",
        "issue__title",
    )


admin.site.register(IssueUserInterest, IssueUserInterestAdmin)
