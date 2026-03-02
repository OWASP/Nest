"""Project health metrics model."""

from functools import cached_property

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Coalesce, ExtractMonth, TruncDate
from django.utils import timezone

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.owasp.api.internal.nodes.project_health_stats import ProjectHealthStatsNode
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements

HEALTH_SCORE_THRESHOLD_HEALTHY = 75
HEALTH_SCORE_THRESHOLD_NEED_ATTENTION = 50


class ProjectHealthMetrics(BulkSaveModel, TimestampedModel):
    """Project health metrics model."""

    class Meta:
        """Model options."""

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
    def age_days_requirement(self) -> int:
        """Get the age requirement for the project."""
        return self.project_requirements.age_days if self.project_requirements else 0

    @property
    def last_commit_days(self) -> int:
        """Calculate days since last commit."""
        return (timezone.now() - self.last_committed_at).days if self.last_committed_at else 0

    @property
    def last_commit_days_requirement(self) -> int:
        """Get the last commit requirement for the project."""
        return self.project_requirements.last_commit_days if self.project_requirements else 0

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
        return self.project_requirements.last_pull_request_days if self.project_requirements else 0

    @property
    def last_release_days(self) -> int:
        """Calculate days since last release."""
        return (timezone.now() - self.last_released_at).days if self.last_released_at else 0

    @property
    def last_release_days_requirement(self) -> int:
        """Get the last release requirement for the project."""
        return self.project_requirements.last_release_days if self.project_requirements else 0

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
        return (
            self.project_requirements.owasp_page_last_update_days
            if self.project_requirements
            else 0
        )

    @cached_property
    def project_requirements(self) -> ProjectHealthRequirements | None:
        """Get the project health requirements for the project's level."""
        return ProjectHealthRequirements.objects.filter(level=self.project.level).first()

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
        # To have a queryset that supports further filtering/ordering,
        # we use a subquery to get the latest metrics per project.
        return ProjectHealthMetrics.objects.filter(
            id__in=ProjectHealthMetrics.objects.filter(project__is_active=True)
            .select_related("project")
            .order_by("project_id", "-nest_created_at")
            .distinct("project_id")
            .values_list("id", flat=True)
        )

    @staticmethod
    def get_stats() -> ProjectHealthStatsNode:
        """Get overall project health stats.

        Returns:
            ProjectHealthStatsNode: The overall health stats of all projects.

        """
        stats = ProjectHealthMetrics.get_latest_health_metrics().aggregate(
            projects_count_healthy=models.Count(
                "id", filter=models.Q(score__gte=HEALTH_SCORE_THRESHOLD_HEALTHY)
            ),
            projects_count_need_attention=models.Count(
                "id",
                filter=models.Q(
                    score__lt=HEALTH_SCORE_THRESHOLD_HEALTHY,
                    score__gte=HEALTH_SCORE_THRESHOLD_NEED_ATTENTION,
                ),
            ),
            projects_count_unhealthy=models.Count(
                "id", filter=models.Q(score__lt=HEALTH_SCORE_THRESHOLD_NEED_ATTENTION)
            ),
            projects_count_total=models.Count("id"),
            average_score=Coalesce(models.Avg("score"), 0.0),
            total_contributors=Coalesce(models.Sum("contributors_count"), 0),
            total_forks=Coalesce(models.Sum("forks_count"), 0),
            total_stars=Coalesce(models.Sum("stars_count"), 0),
        )
        total = stats["projects_count_total"] or 1  # Avoid division by zero
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
        months = []
        scores = []
        for entry in monthly_overall_metrics:
            months.append(entry["month"])
            scores.append(entry["score"])

        return ProjectHealthStatsNode(
            average_score=stats["average_score"],
            # We use all metrics instead of latest metrics to get the monthly trend
            monthly_overall_scores=scores,
            monthly_overall_scores_months=months,
            projects_count_healthy=stats["projects_count_healthy"],
            projects_count_need_attention=stats["projects_count_need_attention"],
            projects_count_unhealthy=stats["projects_count_unhealthy"],
            projects_percentage_healthy=(stats["projects_count_healthy"] / total) * 100,
            projects_percentage_need_attention=(
                (stats["projects_count_need_attention"] / total) * 100
            ),
            projects_percentage_unhealthy=(stats["projects_count_unhealthy"] / total) * 100,
            total_contributors=(stats["total_contributors"]),
            total_forks=(stats["total_forks"]),
            total_stars=(stats["total_stars"]),
        )
