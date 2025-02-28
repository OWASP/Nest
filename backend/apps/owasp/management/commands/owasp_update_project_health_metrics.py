"""A command to update OWASP project health metrics data."""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.utils import timezone

from apps.owasp.models.project import Project
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements


class Command(BaseCommand):
    help = "Update health metrics for OWASP projects."

    def add_arguments(self, parser):
        parser.add_argument("--offset", default=0, required=False, type=int)

    def calculate_health_score(self, metrics, requirements):
        """Calculate health score based on various metrics and thresholds using all parameters."""
        score = 0
        now = timezone.now()
        weight = 100 / 15  # 15 conditions, equal weighting

        if metrics.contributors_count >= requirements.contributors_count:
            score += weight

        if metrics.created_at and (now - metrics.created_at).days >= requirements.age_days:
            score += weight

        if metrics.forks_count >= requirements.forks_count:
            score += weight

        if (
            metrics.last_released_at
            and (now - metrics.last_released_at).days <= requirements.last_release_days
        ):
            score += weight

        if (
            metrics.last_committed_at
            and (now - metrics.last_committed_at).days <= requirements.last_commit_days
        ):
            score += weight

        if metrics.open_issues_count <= requirements.open_issues_count:
            score += weight

        if metrics.open_pull_requests_count <= requirements.open_pull_requests_count:
            score += weight

        if (
            metrics.owasp_page_last_updated_at
            and (now - metrics.owasp_page_last_updated_at).days
            <= requirements.owasp_page_last_update_days
        ):
            score += weight

        if (
            metrics.pull_request_last_created_at
            and (now - metrics.pull_request_last_created_at).days
            <= requirements.last_pull_request_days
        ):
            score += weight

        if metrics.recent_releases_count >= requirements.recent_releases_count:
            score += weight

        if metrics.stars_count >= requirements.stars_count:
            score += weight

        if metrics.total_pull_request_count >= requirements.total_pull_requests_count:
            score += weight

        if metrics.total_releases_count >= requirements.total_releases_count:
            score += weight

        if metrics.unanswered_issues_count <= requirements.unanswered_issues_count:
            score += weight

        if metrics.unassigned_issues_count <= requirements.unassigned_issues_count:
            score += weight

        return min(score, 100)

    def get_pull_request_metrics(self, project):
        """Aggregate pull request metrics across all repositories."""
        pr_metrics = project.repositories.aggregate(
            total_prs=Count("pull_requests"),
            open_prs=Count("pull_requests", filter=Q(pull_requests__state="open")),
        )

        latest_pr = None
        for repo in project.repositories.all():
            repo_latest_pr = repo.pull_requests.order_by("-created_at").first()
            if repo_latest_pr and (
                not latest_pr or repo_latest_pr.created_at > latest_pr.created_at
            ):
                latest_pr = repo_latest_pr

        return {
            "total_prs": pr_metrics["total_prs"],
            "open_prs": pr_metrics["open_prs"],
            "latest_pr_date": latest_pr.created_at if latest_pr else None,
        }

    def get_issue_metrics(self, project, requirements):
        """Aggregate issue metrics across all repositories."""
        now = timezone.now()
        window_start = now - timedelta(days=requirements.recent_releases_time_window_days)

        return project.repositories.aggregate(
            total_issues=Count("issues"),
            unanswered_issues=Count(
                "issues", filter=Q(issues__comments_count=0, issues__state="open")
            ),
            unassigned_issues=Count(
                "issues", filter=Q(issues__assignee__isnull=True, issues__state="open")
            ),
            recent_releases=Count(
                "releases", filter=Q(releases__published_at__year__gte=window_start)
            ),
        )

    def handle(self, *args, **options):
        active_projects = Project.active_projects.order_by("-created_at")
        active_projects_count = active_projects.count()
        offset = options["offset"]
        metrics_to_update = []

        try:
            for idx, project in enumerate(active_projects[offset:]):
                prefix = f"{idx + offset + 1} of {active_projects_count}"
                print(f"{prefix:<10} {project.owasp_url}")

                requirements = ProjectHealthRequirements.objects.get(level=project.level)
                metrics, _ = ProjectHealthMetrics.objects.get_or_create(project=project)

                metrics.contributors_count = project.contributors_count
                metrics.created_at = project.created_at
                metrics.forks_count = project.forks_count
                metrics.stars_count = project.stars_count
                metrics.last_committed_at = project.pushed_at
                metrics.last_released_at = project.released_at
                metrics.open_issues_count = project.open_issues_count

                pr_metrics = self.get_pull_request_metrics(project)
                metrics.total_pull_request_count = pr_metrics["total_prs"]
                metrics.open_pull_requests_count = pr_metrics["open_prs"]
                metrics.pull_request_last_created_at = pr_metrics["latest_pr_date"]

                issue_metrics = self.get_issue_metrics(project, requirements)
                metrics.total_issues_count = issue_metrics["total_issues"]
                metrics.unanswered_issues_count = issue_metrics["unanswered_issues"]
                metrics.unassigned_issues_count = issue_metrics["unassigned_issues"]
                metrics.recent_releases_count = issue_metrics["recent_releases"]
                metrics.total_releases_count = project.releases_count

                metrics.owasp_page_last_updated_at = project.updated_at

                metrics.score = self.calculate_health_score(metrics, requirements)
                metrics_to_update.append(metrics)

            ProjectHealthMetrics.objects.bulk_update(
                metrics_to_update,
                fields=[
                    "contributors_count",
                    "created_at",
                    "forks_count",
                    "last_released_at",
                    "last_committed_at",
                    "open_issues_count",
                    "open_pull_requests_count",
                    "owasp_page_last_updated_at",
                    "pull_request_last_created_at",
                    "recent_releases_count",
                    "score",
                    "stars_count",
                    "total_issues_count",
                    "total_pull_request_count",
                    "total_releases_count",
                    "unanswered_issues_count",
                    "unassigned_issues_count",
                ],
            )

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error updating metrics: {e!s}"))
            raise
