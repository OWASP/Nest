"""A command to update OWASP project health metrics scores."""

from django.core.management.base import BaseCommand

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements


class Command(BaseCommand):
    help = "Update OWASP project health metrics score."

    def handle(self, *args, **options):
        metrics = ProjectHealthMetrics.objects.filter(score__isnull=True)
        weight_mapping = {
            "age_days": (6.0, -1),
            "contributors_count": (6.0, 1),
            "forks_count": (6.0, 1),
            "last_release_days": (6.0, -1),
            "last_commit_days": (6.0, -1),
            "open_issues_count": (6.0, -1),
            "open_pull_requests_count": (6.0, 1),
            "owasp_page_last_update_days": (6.0, -1),
            "last_pull_request_days": (6.0, -1),
            "recent_releases_count": (6.0, 1),
            "stars_count": (6.0, 1),
            "total_pull_requests_count": (6.0, 1),
            "total_releases_count": (6.0, 1),
            "unanswered_issues_count": (6.0, -1),
            "unassigned_issues_count": (6.0, -1),
        }
        to_save = []
        for metric in metrics:
            # Calculate the score based on requirements
            self.stdout.write(
                self.style.NOTICE(f"Updating score for project: {metric.project.name}")
            )
            requirements = ProjectHealthRequirements.objects.get(level=metric.project.level)

            score = 0.0
            for field, (weight, direction) in weight_mapping.items():
                metric_value = getattr(metric, field)
                requirement_value = getattr(requirements, field)

                if (metric_value >= requirement_value and direction == 1) or (
                    metric_value <= requirement_value and direction == -1
                ):
                    score += weight

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
