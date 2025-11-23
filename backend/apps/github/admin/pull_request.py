"""GitHub app PullRequest model admin."""

from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.github.models.pull_request import PullRequest


class PullRequestAdmin(admin.ModelAdmin):
    """Admin for PullRequest model."""

    autocomplete_fields = (
        "assignees",
        "author",
        "labels",
        "related_issues",
        "repository",
    )
    list_display = (
        "repository",
        "title",
        "state",
        "custom_field_github_url",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "state",
        "merged_at",
    )
    search_fields = (
        "author__login",
        "repository__name",
        "title",
    )

    def custom_field_github_url(self, obj: PullRequest) -> str:
        """Pull Request GitHub URL.

        Args:
            obj (PullRequest): The pull request instance.

        Returns:
            str: A safe HTML link to the pull request on GitHub.

        """
        return mark_safe(f"<a href='{obj.url}' target='_blank'>↗️</a>")  # noqa: S308

    custom_field_github_url.short_description = "GitHub 🔗"


admin.site.register(PullRequest, PullRequestAdmin)
