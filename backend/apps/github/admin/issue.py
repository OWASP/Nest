"""GitHub app Issue model admin."""

from django.contrib import admin
from django.utils.html import format_html

from apps.github.models.issue import Issue


class IssueAdmin(admin.ModelAdmin):
    """Admin for Issue model."""

    autocomplete_fields = (
        "repository",
        "author",
        "assignees",
        "labels",
    )
    list_display = (
        "repository",
        "created_at",
        "title",
        "level",
        "custom_field_github_url",
    )
    list_filter = (
        "state",
        "is_locked",
    )
    search_fields = ("title",)

    def custom_field_github_url(self, obj) -> str:
        """Issue GitHub URL.

        Args:
            obj (Issue): The issue instance.

        Returns:
            str: A safe HTML link to the issue on GitHub.

        """
        return format_html("<a href='{}' target='_blank'>↗️</a>", obj.url)

    custom_field_github_url.short_description = "GitHub 🔗"


admin.site.register(Issue, IssueAdmin)
