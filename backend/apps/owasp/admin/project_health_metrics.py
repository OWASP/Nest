"""Project health metrics admin configuration."""

from django.contrib import admin

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics

from .mixins import StandardOwaspAdminMixin


class ProjectHealthMetricsAdmin(admin.ModelAdmin, StandardOwaspAdminMixin):
    """Admin for ProjectHealthMetrics model."""

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
        """
        Return the name of the related project for display purposes.

        Used in the admin list view to show a readable project label instead
        of the raw project foreign key reference.
        
        """
        return obj.project.name if obj.project else "N/A"


admin.site.register(ProjectHealthMetrics, ProjectHealthMetricsAdmin)
