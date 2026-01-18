"""Project health metrics model."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import ExtractMonth, TruncDate
from django.utils import timezone

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.owasp.api.internal.nodes.project_health_stats import ProjectHealthStatsNode
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements

HEALTH_SCORE_THRESHOLD_HEALTHY = 75
HEALTH_SCORE_THRESHOLD_NEED_ATTENTION = 50


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
    is_level_non_compliant = models.BooleanField(
        verbose_name="Is level non-compliant",
        default=False,
        help_text="Indicates if the project level does not match the official OWASP level",
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
    def age_days_requirement(self) -> int:
        """Get the age requirement for the project."""
        return self.project_requirements.age_days

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
    def last_pull_request_days_requirement(self) -> int:
        """Get the last pull request requirement for the project."""
        return self.project_requirements.last_pull_request_days

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
    def owasp_page_last_update_days_requirement(self) -> int:
        """Get the OWASP page last update requirement for the project."""
        return self.project_requirements.owasp_page_last_update_days

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
    def get_latest_health_metrics() -> models.QuerySet["ProjectHealthMetrics"]:
        """Get latest health metrics for each project.

        Returns:
            QuerySet[ProjectHealthMetrics]: QuerySet of project health metrics.

        """
        return ProjectHealthMetrics.objects.filter(
            nest_created_at=models.Subquery(
                ProjectHealthMetrics.objects.filter(project=models.OuterRef("project"))
                .order_by("-nest_created_at")
                .values("nest_created_at")[:1]
            ),
            project__is_active=True,
        )

    @staticmethod
    def get_stats() -> ProjectHealthStatsNode:
        """Get overall project health stats.

        Returns:
            ProjectHealthStatsNode: The overall health stats of all projects.

        """
        metrics = ProjectHealthMetrics.get_latest_health_metrics()

        projects_count_healthy = metrics.filter(
            score__gte=HEALTH_SCORE_THRESHOLD_HEALTHY,
        ).count()
        projects_count_need_attention = metrics.filter(
            score__lt=HEALTH_SCORE_THRESHOLD_HEALTHY,
            score__gte=HEALTH_SCORE_THRESHOLD_NEED_ATTENTION,
        ).count()
        projects_count_unhealthy = metrics.filter(
            score__lt=HEALTH_SCORE_THRESHOLD_NEED_ATTENTION
        ).count()

        projects_count_total = metrics.count() or 1  # Avoid division by zero

        aggregation = metrics.aggregate(
            average_score=models.Avg("score"),
            total_contributors=models.Sum("contributors_count"),
            total_forks=models.Sum("forks_count"),
            total_stars=models.Sum("stars_count"),
        )
        monthly_overall_metrics = (
            ProjectHealthMetrics.objects.annotate(month=ExtractMonth("nest_created_at"))
            .filter(
                nest_created_at__gte=timezone.now() - timezone.timedelta(days=365)
            )  # Last year data
            .order_by("month")
            .values("month")
            .distinct()
            .annotate(
                score=models.Avg("score"),
            )
        )
        return ProjectHealthStatsNode(
            average_score=aggregation.get("average_score", 0.0),
            # We use all metrics instead of latest metrics to get the monthly trend
            monthly_overall_scores=list(monthly_overall_metrics.values_list("score", flat=True)),
            monthly_overall_scores_months=list(
                monthly_overall_metrics.values_list("month", flat=True)
            ),
            projects_count_healthy=projects_count_healthy,
            projects_count_need_attention=projects_count_need_attention,
            projects_count_unhealthy=projects_count_unhealthy,
            projects_percentage_healthy=(projects_count_healthy / projects_count_total) * 100,
            projects_percentage_need_attention=(
                (projects_count_need_attention / projects_count_total) * 100
            ),
            projects_percentage_unhealthy=(projects_count_unhealthy / projects_count_total) * 100,
            total_contributors=(aggregation.get("total_contributors", 0)),
            total_forks=(aggregation.get("total_forks", 0)),
            total_stars=(aggregation.get("total_stars", 0)),
        )
