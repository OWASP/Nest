"""A command to update OWASP project health metrics score."""

from django.core.management.base import BaseCommand

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements


class Command(BaseCommand):
    help = "Update OWASP project health metrics score."

    def handle(self, *args, **options):
        metrics = ProjectHealthMetrics.objects.all()
        weight_mapping = {
            "age_days": 6.0,
            "contributors_count": 6.0,
            "forks_count": 6.0,
            "last_release_days": 6.0,
            "last_commit_days": 6.0,
            "open_issues_count": 6.0,
            "open_pull_requests_count": 6.0,
            "owasp_page_last_update_days": 6.0,
            "last_pull_request_days": 6.0,
            "recent_releases_count": 6.0,
            "stars_count": 8.0,
            "total_pull_requests_count": 8.0,
            "total_releases_count": 8.0,
            "unanswered_issues_count": 8.0,
            "unassigned_issues_count": 8.0,
        }
        for metric in metrics:
            try:
                # Calculate the score based on requirements
                requirements = ProjectHealthRequirements.objects.get(level=metric.project.level)

                score = 0.0
                for field, weight in weight_mapping.items():
                    metric_value = getattr(metric, field)
                    requirement_value = getattr(requirements, field)

                    if metric_value >= requirement_value:
                        score += weight

                metric.score = score
                metric.save(update_fields=["score"])
                self.stdout.write(
                    self.style.SUCCESS(f"Updated score for project {metric.project.name}: {score}")
                )

            except (AttributeError, ValueError, TypeError) as e:
                self.stdout.write(
                    self.style.ERROR(f"Error updating project {metric.project.name}: {e}")
                )
