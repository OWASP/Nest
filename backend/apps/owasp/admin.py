"""OWASP app admin."""

from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.event import Event
from apps.owasp.models.project import Project
from apps.owasp.models.sponsor import Sponsor
from apps.owasp.models.snapshot import Snapshot


class GenericEntityAdminMixin:
    def custom_field_github_urls(self, obj):
        """Entity GitHub URLs."""
        urls = [
            f"<a href='https://github.com/{repository.owner.login}/"
            f"{repository.key}' target='_blank'>↗️</a>"
            for repository in (
                obj.repositories.all() if hasattr(obj, "repositories") else [obj.owasp_repository]
            )
        ]

        return mark_safe(" ".join(urls))  # noqa: S308

    def custom_field_owasp_url(self, obj):
        """Entity OWASP URL."""
        return mark_safe(  # noqa: S308
            f"<a href='https://owasp.org/{obj.key}' target='_blank'>↗️</a>"
        )

    custom_field_github_urls.short_description = "GitHub 🔗"
    custom_field_owasp_url.short_description = "OWASP 🔗"


class ChapterAdmin(admin.ModelAdmin, GenericEntityAdminMixin):
    autocomplete_fields = ("owasp_repository",)
    list_display = (
        "name",
        "region",
        "custom_field_owasp_url",
        "custom_field_github_urls",
    )
    list_filter = (
        "is_active",
        "country",
        "region",
    )
    search_fields = ("name", "key")


class CommitteeAdmin(admin.ModelAdmin):
    autocomplete_fields = ("owasp_repository",)
    search_fields = ("name",)


class EventAdmin(admin.ModelAdmin):
    autocomplete_fields = ("owasp_repository",)
    list_display = ("name",)
    search_fields = ("name",)


class ProjectAdmin(admin.ModelAdmin, GenericEntityAdminMixin):
    autocomplete_fields = (
        "organizations",
        "owasp_repository",
        "owners",
        "repositories",
    )
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

    def custom_field_name(self, obj):
        """Project custom name."""
        return f"{obj.name or obj.key}"

    custom_field_name.short_description = "Name"

    
class SnapshotAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        "new_chapters",
        "new_issues",
        "new_projects",
        "new_releases",
        "new_users",
    )
    list_display = (
        "start_at",
        "end_at",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "status",
        "start_at",
        "end_at",
    )
    ordering = ("-start_at",)
    search_fields = (
        "status",
        "error_message",
    )
    
    
class SponsorAdmin(admin.ModelAdmin):
    """Admin configuration for Sponsor model."""

    list_display = (
        "name",
        "sort_name",
        "sponsor_type",
        "is_member",
        "member_type",
    )

    search_fields = (
        "name",
        "sort_name",
        "description",
    )

    list_filter = (
        "sponsor_type",
        "is_member",
        "member_type",
    )

    fieldsets = (
        ("Basic Information", {"fields": ("name", "sort_name", "description")}),
        ("URLs and Images", {"fields": ("url", "job_url", "image_path")}),
        ("Status", {"fields": ("is_member", "member_type", "sponsor_type")}),
    )

admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Committee, CommitteeAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Snapshot, SnapshotAdmin)
admin.site.register(Sponsor, SponsorAdmin)