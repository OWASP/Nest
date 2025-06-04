"""Project health metrics model."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.common.models import TimestampedModel


class ProjectHealthMetrics(TimestampedModel):
    """Project health metrics model."""

    class Meta:
        db_table = "owasp_project_health_metrics"
        verbose_name_plural = "Project Health Metrics"

    project = models.OneToOneField(
        "owasp.Project",
        on_delete=models.CASCADE,
        related_name="health_metrics",
    )

    contributors_count = models.PositiveIntegerField(verbose_name="Contributors", default=0)
    created_at = models.DateTimeField(verbose_name="Created at", blank=True, null=True)
    forks_count = models.PositiveIntegerField(verbose_name="Forks", default=0)
    is_funding_requirements_compliant = models.BooleanField(
        verbose_name="Is funding requirements compliant", default=False
    )
    is_project_leaders_requirements_compliant = models.BooleanField(
        verbose_name="Is project leaders requirements compliant", default=False
    )
    last_released_at = models.DateTimeField(verbose_name="Last released at", blank=True, null=True)
    last_committed_at = models.DateTimeField(
        verbose_name="Last committed at", blank=True, null=True
    )
    open_issues_count = models.PositiveIntegerField(verbose_name="Open issues", default=0)
    open_pull_requests_count = models.PositiveIntegerField(
        verbose_name="Open pull requests", default=0
    )
    owasp_page_last_updated_at = models.DateTimeField(
        verbose_name="OWASP page last updated at", blank=True, null=True
    )
    pull_request_last_created_at = models.DateTimeField(
        verbose_name="Pull request last created at", blank=True, null=True
    )
    recent_releases_count = models.PositiveIntegerField(verbose_name="Recent releases", default=0)
    # score of projects health between 0 and 100(float value)
    score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Project health score (0-100)",
    )
    stars_count = models.PositiveIntegerField(verbose_name="Stars", default=0)
    total_issues_count = models.PositiveIntegerField(verbose_name="Total issues", default=0)
    total_pull_requests_count = models.PositiveIntegerField(
        verbose_name="Total pull requests", default=0
    )
    total_releases_count = models.PositiveIntegerField(verbose_name="Total releases", default=0)
    unanswered_issues_count = models.PositiveIntegerField(
        verbose_name="Unanswered issues", default=0
    )
    unassigned_issues_count = models.PositiveIntegerField(
        verbose_name="Unassigned issues", default=0
    )

    @property
    def age_days(self) -> int:
        """Calculate project age in days."""
        if self.created_at:
            return (timezone.now() - self.created_at).days
        return 0

    @property
    def last_commit_days(self) -> int:
        """Calculate days since last commit."""
        if self.last_committed_at:
            return (timezone.now() - self.last_committed_at).days
        return 0

    @property
    def last_pull_request_days(self) -> int:
        """Calculate days since last pull request."""
        if self.pull_request_last_created_at:
            return (timezone.now() - self.pull_request_last_created_at).days
        return 0

    @property
    def last_release_days(self) -> int:
        """Calculate days since last release."""
        if self.last_released_at:
            return (timezone.now() - self.last_released_at).days
        return 0

    @property
    def owasp_page_last_update_days(self) -> int:
        """Calculate days since OWASP page last update."""
        if self.owasp_page_last_updated_at:
            return (timezone.now() - self.owasp_page_last_updated_at).days
        return 0

    def __str__(self) -> str:
        """Project health metrics human readable representation."""
        return f"Health Metrics for {self.project.name}"
