"""Mentorship app IssueUserInterest admin."""

from django.contrib import admin

from apps.mentorship.models import IssueUserInterest


class IssueUserInterestAdmin(admin.ModelAdmin):
    """IssueUserInterest admin."""

    list_display = ("module", "issue")
    search_fields = ("module__name", "users__login", "issue__title")
    list_filter = ("module",)


admin.site.register(IssueUserInterest, IssueUserInterestAdmin)
