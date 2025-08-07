"""GitHub app Issue model admin."""

from django.contrib import admin
from django.utils.safestring import mark_safe

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
        return mark_safe(f"<a href='{obj.url}' target='_blank'>↗️</a>")  # noqa: S308

    custom_field_github_url.short_description = "GitHub 🔗"


admin.site.register(Issue, IssueAdmin)
