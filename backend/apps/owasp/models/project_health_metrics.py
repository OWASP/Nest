"""Project health metrics model."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.owasp.graphql.nodes.health_stats import HealthStatsNode
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements


class ProjectHealthMetrics(BulkSaveModel, TimestampedModel):
    """Project health metrics model."""

    class Meta:
        db_table = "owasp_project_health_metrics"
        verbose_name_plural = "Project Health Metrics"

        constraints = (
            models.UniqueConstraint(
                TruncDate("nest_created_at"),
                models.F("project"),
                name="unique_daily_project_health_metrics",
            ),
        )

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
    def last_commit_days_requirement(self) -> int:
        """Get the last commit requirement for the project."""
        return self.project_requirements.last_commit_days

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
    def last_release_days_requirement(self) -> int:
        """Get the last release requirement for the project."""
        return self.project_requirements.last_release_days

    @property
    def owasp_page_last_update_days(self) -> int:
        """Calculate days since OWASP page last update."""
        return (
            (timezone.now() - self.owasp_page_last_updated_at).days
            if self.owasp_page_last_updated_at
            else 0
        )

    @property
    def project_requirements(self) -> ProjectHealthRequirements:
        """Get the project health requirements for the project's level."""
        return ProjectHealthRequirements.objects.get(level=self.project.level)

    @staticmethod
    def bulk_save(metrics: list, fields: list | None = None) -> None:  # type: ignore[override]
        """Bulk save method for ProjectHealthMetrics.

        Args:
            metrics (list[ProjectHealthMetrics]): List of ProjectHealthMetrics instances to save.
            fields (list[str], optional): List of fields to update. Defaults to None.

        """
        BulkSaveModel.bulk_save(ProjectHealthMetrics, metrics, fields=fields)

    @staticmethod
    def get_distinct_health_metrics() -> models.QuerySet["ProjectHealthMetrics"]:
        """Get distinct project health metrics.

        Returns:
            QuerySet[ProjectHealthMetrics]: QuerySet of distinct project health metrics.

        """
        return ProjectHealthMetrics.objects.filter(
            nest_created_at=models.Subquery(
                ProjectHealthMetrics.objects.filter(project=models.OuterRef("project"))
                .order_by("-nest_created_at")
                .values("nest_created_at")[:1]
            )
        )

    @staticmethod
    def get_overall_stats() -> HealthStatsNode:
        """Get overall project health stats.

        Returns:
            dict: The overall health stats of all projects.

        """
        metrics = ProjectHealthMetrics.get_distinct_health_metrics()
        total_projects_count = metrics.count()
        healthy_projects_count = metrics.filter(score__gte=75).count()
        projects_needing_attention_count = metrics.filter(score__lt=75, score__gte=50).count()
        unhealthy_projects_count = metrics.filter(score__lt=50).count()
        return HealthStatsNode(
            healthy_projects_count=healthy_projects_count,
            healthy_projects_percentage=(healthy_projects_count / total_projects_count) * 100,
            projects_needing_attention_count=projects_needing_attention_count,
            projects_needing_attention_percentage=(
                projects_needing_attention_count / total_projects_count
            )
            * 100,
            unhealthy_projects_count=unhealthy_projects_count,
            unhealthy_projects_percentage=(unhealthy_projects_count / total_projects_count) * 100,
            average_score=metrics.aggregate(average_score=models.Avg("score"))["average_score"]
            or 0.0,
            total_stars=metrics.aggregate(total_stars=models.Sum("stars_count"))["total_stars"]
            or 0,
            total_forks=metrics.aggregate(total_forks=models.Sum("forks_count"))["total_forks"]
            or 0,
            total_contributors=metrics.aggregate(
                total_contributors=models.Sum("contributors_count")
            )["total_contributors"]
            or 0,
            monthly_overall_scores=list(
                metrics.annotate(month=models.functions.ExtractMonth("nest_created_at"))
                .order_by("month")
                .values("month")
                .distinct()
                .annotate(score=models.Avg("score"))
                .values_list("score", flat=True)
            ),
        )
