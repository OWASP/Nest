"""Project health requirements model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.owasp.models.project import Project


class ProjectHealthRequirements(TimestampedModel):
    """Project health requirements model."""

    class Meta:
        db_table = "owasp_project_health_requirements"
        verbose_name_plural = "Project Health Requirements"
        ordering = ["level"]

    level = models.CharField(
        max_length=10,
        choices=Project.ProjectLevel.choices,
        unique=True,
        verbose_name="Project Level",
    )

    age_days = models.PositiveIntegerField(verbose_name="Project age (days)", default=0)
    contributors_count = models.PositiveIntegerField(verbose_name="Contributors", default=0)
    forks_count = models.PositiveIntegerField(verbose_name="Forks", default=0)
    is_funding_requirements_compliant = models.BooleanField(
        verbose_name="Is funding requirements compliant", default=True
    )
    is_leader_requirements_compliant = models.BooleanField(
        verbose_name="Is leader requirements compliant", default=True
    )
    last_release_days = models.PositiveIntegerField(
        verbose_name="Days since last release", default=0
    )
    last_commit_days = models.PositiveIntegerField(
        verbose_name="Days since last commit", default=0
    )
    open_issues_count = models.PositiveIntegerField(verbose_name="Open issues", default=0)
    open_pull_requests_count = models.PositiveIntegerField(verbose_name="Open PRs", default=0)
    owasp_page_last_update_days = models.PositiveIntegerField(
        verbose_name="Days since OWASP update", default=0
    )
    last_pull_request_days = models.PositiveIntegerField(
        verbose_name="Days since last PR", default=0
    )
    recent_releases_count = models.PositiveIntegerField(verbose_name="Recent releases", default=0)
    recent_releases_time_window_days = models.PositiveIntegerField(
        verbose_name="Recent releases window", default=0
    )
    stars_count = models.PositiveIntegerField(verbose_name="Stars", default=0)
    total_pull_requests_count = models.PositiveIntegerField(verbose_name="Total PRs", default=0)
    total_releases_count = models.PositiveIntegerField(verbose_name="Total releases", default=0)
    unanswered_issues_count = models.PositiveIntegerField(
        verbose_name="Unanswered issues", default=0
    )
    unassigned_issues_count = models.PositiveIntegerField(
        verbose_name="Unassigned issues", default=0
    )

    def __str__(self) -> str:
        """Project health requirements human readable representation."""
        return f"Health Requirements for {self.get_level_display()} Projects"
