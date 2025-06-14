"""OWASP app admin."""

from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.event import Event
from apps.owasp.models.post import Post
from apps.owasp.models.project import Project
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements
from apps.owasp.models.snapshot import Snapshot
from apps.owasp.models.sponsor import Sponsor


class GenericEntityAdminMixin:
    def get_queryset(self, request):
        """Get queryset."""
        return super().get_queryset(request).prefetch_related("repositories")

    def custom_field_github_urls(self, obj):
        """Entity GitHub URLs."""
        if not hasattr(obj, "repositories"):
            return mark_safe(  # noqa: S308
                f"<a href='https://github.com/{obj.owasp_repository.owner.login}/"
                f"{obj.owasp_repository.key}' target='_blank'>↗️</a>"
            )

        urls = [
            f"<a href='https://github.com/{repository.owner.login}/"
            f"{repository.key}' target='_blank'>↗️</a>"
            for repository in obj.repositories.all()
        ]

        return mark_safe(" ".join(urls))  # noqa: S308

    def custom_field_owasp_url(self, obj):
        """Entity OWASP URL."""
        return mark_safe(  # noqa: S308
            f"<a href='https://owasp.org/{obj.key}' target='_blank'>↗️</a>"
        )

    custom_field_github_urls.short_description = "GitHub 🔗"
    custom_field_owasp_url.short_description = "OWASP 🔗"


class LeaderAdminMixin:
    """Admin mixin for entities that can have leaders."""

    actions = ("approve_suggested_leaders",)
    filter_horizontal = ("suggested_leaders",)

    def approve_suggested_leaders(self, request, queryset):
        """Approve suggested leaders for selected entities."""
        for entity in queryset:
            suggestions = entity.suggested_leaders.all()
            entity.leaders.add(*suggestions)
            self.message_user(
                request,
                f"Approved {suggestions.count()} leader suggestions for {entity.name}",
                messages.SUCCESS,
            )

    approve_suggested_leaders.short_description = "Approve suggested leaders"


class ChapterAdmin(admin.ModelAdmin, GenericEntityAdminMixin, LeaderAdminMixin):
    autocomplete_fields = (
        "leaders",
        "owasp_repository",
    )
    list_display = (
        "name",
        "created_at",
        "updated_at",
        "region",
        "custom_field_owasp_url",
        "custom_field_github_urls",
    )
    list_filter = (
        "is_active",
        "is_leaders_policy_compliant",
        "country",
        "region",
    )
    search_fields = ("name", "key")


class CommitteeAdmin(admin.ModelAdmin, GenericEntityAdminMixin, LeaderAdminMixin):
    autocomplete_fields = (
        "leaders",
        "owasp_repository",
    )
    search_fields = ("name",)


class EventAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "suggested_location",
    )
    search_fields = ("name",)


class PostAdmin(admin.ModelAdmin):
    """Admin configuration for Post model."""

    list_display = (
        "author_name",
        "published_at",
        "title",
    )
    search_fields = (
        "author_image_url",
        "author_name",
        "published_at",
        "title",
        "url",
    )


class ProjectAdmin(admin.ModelAdmin, GenericEntityAdminMixin, LeaderAdminMixin):
    autocomplete_fields = (
        "leaders",
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


class ProjectHealthMetricsAdmin(admin.ModelAdmin):
    autocomplete_fields = ("project",)
    list_filter = (
        "project__level",
        "nest_created_at",
    )
    list_display = (
        "project",
        "nest_created_at",
        "score",
        "contributors_count",
        "stars_count",
        "forks_count",
        "open_issues_count",
        "open_pull_requests_count",
        "recent_releases_count",
    )
    search_fields = ("project__name",)

    def project(self, obj):
        """Display project name."""
        return obj.project.name if obj.project else "N/A"


class SnapshotAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        "new_chapters",
        "new_issues",
        "new_projects",
        "new_releases",
        "new_users",
    )
    list_display = (
        "title",
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
        "title",
        "key",
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
        ("URLs and Images", {"fields": ("url", "job_url", "image_url")}),
        ("Status", {"fields": ("is_member", "member_type", "sponsor_type")}),
    )


admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Committee, CommitteeAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectHealthMetrics, ProjectHealthMetricsAdmin)
admin.site.register(ProjectHealthRequirements)
admin.site.register(Snapshot, SnapshotAdmin)
admin.site.register(Sponsor, SponsorAdmin)
