"""A command to update OWASP project health metrics scores."""

from django.core.management.base import BaseCommand

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements


class Command(BaseCommand):
    help = "Update OWASP project health metrics score."

    def handle(self, *args, **options):
        metrics = ProjectHealthMetrics.objects.filter(score__isnull=True).select_related("project")
        forward_fields = [
            "contributors_count",
            "forks_count",
            "open_pull_requests_count",
            "recent_releases_count",
            "stars_count",
            "total_pull_requests_count",
            "total_releases_count",
        ]
        backward_fields = [
            "age_days",
            "last_commit_days",
            "last_pull_request_days",
            "last_release_days",
            "open_issues_count",
            "owasp_page_last_update_days",
            "unanswered_issues_count",
            "unassigned_issues_count",
        ]
        to_save = []
        requirements_cache = {}
        for metric in metrics:
            # Calculate the score based on requirements
            self.stdout.write(
                self.style.NOTICE(f"Updating score for project: {metric.project.name}")
            )
            level = metric.project.level
            if level not in requirements_cache:
                requirements_cache[level] = ProjectHealthRequirements.objects.get(level=level)

            requirements = requirements_cache[level]
            score = 0.0
            for field in forward_fields:
                if getattr(metric, field) >= getattr(requirements, field):
                    score += 6.0
            for field in backward_fields:
                if getattr(metric, field) <= getattr(requirements, field):
                    score += 6.0

            # Evaluate compliance with funding and leaders requirements
            if metric.is_funding_requirements_compliant:
                score += 5.0
            if metric.is_project_leaders_requirements_compliant:
                score += 5.0

            metric.score = score
            to_save.append(metric)
        ProjectHealthMetrics.bulk_save(to_save, fields=["score"])
        self.stdout.write(
            self.style.SUCCESS("Updated projects health metrics score successfully.")
        )
