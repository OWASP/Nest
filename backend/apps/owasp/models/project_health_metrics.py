"""Project health metrics model."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.common.models import BulkSaveModel, TimestampedModel


class ProjectHealthMetrics(BulkSaveModel, TimestampedModel):
    """Project health metrics model."""

    class Meta:
        db_table = "owasp_project_health_metrics"
        verbose_name_plural = "Project Health Metrics"

    project = models.ForeignKey(
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
    is_leader_requirements_compliant = models.BooleanField(
        verbose_name="Is leader requirements compliant", default=False
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
    score = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Project health score",
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="0-100",
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

    def __str__(self) -> str:
        """Project health metrics human readable representation."""
        return f"Health Metrics for {self.project.name}"

    @property
    def age_days(self) -> int:
        """Calculate project age in days."""
        return (timezone.now() - self.created_at).days if self.created_at else 0

    @property
    def last_commit_days(self) -> int:
        """Calculate days since last commit."""
        return (timezone.now() - self.last_committed_at).days if self.last_committed_at else 0

    @property
    def last_pull_request_days(self) -> int:
        """Calculate days since last pull request."""
        return (
            (timezone.now() - self.pull_request_last_created_at).days
            if self.pull_request_last_created_at
            else 0
        )

    @property
    def last_release_days(self) -> int:
        """Calculate days since last release."""
        return (timezone.now() - self.last_released_at).days if self.last_released_at else 0

    @property
    def owasp_page_last_update_days(self) -> int:
        """Calculate days since OWASP page last update."""
        return (
            (timezone.now() - self.owasp_page_last_updated_at).days
            if self.owasp_page_last_updated_at
            else 0
        )

    @staticmethod
    def bulk_save(metrics: list, fields: list | None = None) -> None:  # type: ignore[override]
        """Bulk save method for ProjectHealthMetrics.

        Args:
            metrics (list[ProjectHealthMetrics]): List of ProjectHealthMetrics instances to save.
            fields (list[str], optional): List of fields to update. Defaults to None.

        """
        BulkSaveModel.bulk_save(ProjectHealthMetrics, metrics, fields=fields)
