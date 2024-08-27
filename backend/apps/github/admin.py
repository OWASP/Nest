"""Repository app admin."""

from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.github.models import Organization, Release, Repository, User


class RepositoryAdmin(admin.ModelAdmin):
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
        "is_fork",
    )
    ordering = ("-created_at",)
    search_fields = ("name",)

    def custom_field_github_url(self, obj):
        """Repository GitHub URL."""
        return mark_safe(  # noqa: S308
            f"<a href='https://github.com/{obj.owner.login}/{obj.name}' target='_blank'>↗️</a>"
        )

    def custom_field_title(self, obj):
        """Repository title."""
        return f"{obj.owner.login}/{obj.name}"

    custom_field_title.short_description = "Name"
    custom_field_github_url.short_description = "GitHub 🔗"


class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "created_at",
        "updated_at",
        "followers_count",
    )
    search_fields = ("name",)


class ReleaseAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        "author",
        "repository",
    )
    search_fields = ("node_id", "repository__name")


class UserAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "updated_at")
    search_fields = ("name",)


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(Repository, RepositoryAdmin)
admin.site.register(User, UserAdmin)
