"""GitHub app Repository model admin."""

from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.github.models.repository import Repository


class RepositoryAdmin(admin.ModelAdmin):
    """Admin for Repository model."""

    autocomplete_fields = (
        "organization",
        "owner",
    )
    list_display = (
        "custom_field_title",
        "created_at",
        "updated_at",
        "stars_count",
        "forks_count",
        "commits_count",
        "custom_field_github_url",
    )
    list_filter = (
        "is_archived",
        "is_empty",
        "is_owasp_repository",
        "is_owasp_site_repository",
        "has_funding_yml",
        "is_funding_policy_compliant",
        "is_template",
        "is_fork",
        "organization",
    )
    ordering = ("-created_at",)
    search_fields = ("name", "node_id")

    def custom_field_github_url(self, obj) -> str:
        """Repository GitHub URL.

        Args:
            obj (Repository): The repository instance.

        Returns:
            str: A safe HTML link to the repository on GitHub.

        """
        return mark_safe(  # noqa: S308
            f"<a href='https://github.com/{obj.owner.login}/{obj.name}' target='_blank'>↗️</a>"
        )

    def custom_field_title(self, obj: Repository) -> str:
        """Repository title.

        Args:
            obj (Repository): The repository instance.

        Returns:
            str: The formatted repository title as 'owner/repository_name'.

        """
        return f"{obj.owner.login}/{obj.name}"

    custom_field_title.short_description = "Name"
    custom_field_github_url.short_description = "GitHub 🔗"


admin.site.register(Repository, RepositoryAdmin)
