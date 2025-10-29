"""Project admin configuration."""

from django.contrib import admin

from apps.owasp.admin.mixins import (
    EntityChannelInline,
    EntityMemberInline,
    GenericEntityAdminMixin,
)
from apps.owasp.models.project import Project


class ProjectAdmin(admin.ModelAdmin, GenericEntityAdminMixin):
    """Admin for Project model."""

    autocomplete_fields = (
        "organizations",
        "owasp_repository",
        "owners",
        "repositories",
    )
    exclude = (
        "leaders",
        "suggested_leaders",
    )
    inlines = (EntityMemberInline, EntityChannelInline)
    list_display = (
        "custom_field_name",
        "created_at",
        "updated_at",
        "stars_count",
        "forks_count",
        "commits_count",
        "releases_count",
        "custom_field_owasp_url",
        "custom_field_github_urls",
    )
    list_filter = (
        "is_active",
        "is_leaders_policy_compliant",
        "has_active_repositories",
        "level",
        "type",
    )
    ordering = ("-created_at",)
    search_fields = (
        "custom_tags",
        "description",
        "key",
        "languages",
        "leaders_raw",
        "name",
        "topics",
    )

    def custom_field_name(self, obj) -> str:
        """Project custom name."""
        return f"{obj.name or obj.key}"

    custom_field_name.short_description = "Name"


admin.site.register(Project, ProjectAdmin)
