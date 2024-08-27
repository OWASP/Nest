"""OWASP app admin."""

from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.owasp.models import Chapter, Committee, Event, Project


class ChapterAdmin(admin.ModelAdmin):
    autocomplete_fields = ("owasp_repository",)
    list_display = (
        "name",
        "region",
    )
    list_filter = (
        "country",
        "region",
    )
    search_fields = ("name",)


class CommetteeAdmin(admin.ModelAdmin):
    autocomplete_fields = ("owasp_repository",)
    search_fields = ("name",)


class EventAdmin(admin.ModelAdmin):
    autocomplete_fields = ("owasp_repository",)
    list_display = ("name",)
    search_fields = ("name",)


class ProjectAdmin(admin.ModelAdmin):
    autocomplete_fields = ("owasp_repository", "repositories")
    list_display = (
        "custom_field_name",
        "created_at",
        "updated_at",
        "stars_count",
        "forks_count",
        "commits_count",
        "releases_count",
        "custom_field_owasp_url",
        "custom_field_github_url",
    )
    list_filter = (
        "is_active",
        "has_active_repositories",
        "level",
        "type",
    )
    search_fields = (
        "name",
        "description",
        "leaders_raw",
        "languages",
        "topics",
    )

    def custom_field_name(self, obj):
        """Project custom name."""
        return f"{obj.name or obj.key}"

    def custom_field_github_url(self, obj):
        """Project GitHub URL."""
        urls = [
            f"<a href='https://github.com/{repository.owner.login}/"
            f"{repository.key}' target='_blank'>↗️</a>"
            for repository in obj.repositories.all()
        ]

        return mark_safe(" ".join(urls))  # noqa: S308

    def custom_field_owasp_url(self, obj):
        """Project OWASP URL."""
        return mark_safe(  # noqa: S308
            f"<a href='https://owasp.org/{obj.key}' target='_blank'>↗️</a>"
        )

    custom_field_name.short_description = "Name"
    custom_field_github_url.short_description = "GitHub 🔗"
    custom_field_owasp_url.short_description = "OWASP 🔗"


admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Committee, CommetteeAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Project, ProjectAdmin)
