"""A command to update OWASP project health metrics."""

from django.core.management.base import BaseCommand

from apps.owasp.models.project import Project
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


class Command(BaseCommand):
    help = "Update OWASP project health metrics."

    def handle(self, *args, **options):
        metric_project_field_mapping = {
            "contributors_count": "contributors_count",
            "created_at": "created_at",
            "forks_count": "forks_count",
            "is_funding_requirements_compliant": "is_funding_requirements_compliant",
            "is_leader_requirements_compliant": "is_leader_requirements_compliant",
            "last_committed_at": "pushed_at",
            "last_released_at": "released_at",
            "open_issues_count": "open_issues_count",
            "open_pull_requests_count": "open_pull_requests_count",
            "owasp_page_last_updated_at": "owasp_page_last_updated_at",
            "pull_request_last_created_at": "pull_request_last_created_at",
            "recent_releases_count": "recent_releases_count",
            "stars_count": "stars_count",
            "total_issues_count": "issues_count",
            "total_pull_requests_count": "pull_requests_count",
            "total_releases_count": "releases_count",
            "unanswered_issues_count": "unanswered_issues_count",
            "unassigned_issues_count": "unassigned_issues_count",
        }
        project_health_metrics = []
        for project in Project.objects.all():
            self.stdout.write(self.style.NOTICE(f"Evaluating metrics for project: {project.name}"))
            metrics = ProjectHealthMetrics(project=project)

            # Update metrics based on requirements.
            for metric_field, project_field in metric_project_field_mapping.items():
                setattr(metrics, metric_field, getattr(project, project_field))

            project_health_metrics.append(metrics)

        ProjectHealthMetrics.bulk_save(project_health_metrics)
        self.stdout.write(self.style.SUCCESS("Evaluated projects health metrics successfully. "))
