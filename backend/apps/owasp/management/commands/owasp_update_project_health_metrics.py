"""A command to update OWASP project health metrics."""

from django.core.management.base import BaseCommand

from apps.owasp.models.project import Project
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


class Command(BaseCommand):
    help = "Update OWASP project health metrics."

    def handle(self, *args, **options):
        projects = Project.objects.all()
        field_mappings = {
            "contributors_count": "contributors_count",
            "created_at": "created_at",
            "forks_count": "forks_count",
            "last_released_at": "last_released_at",
            "last_committed_at": "last_committed_at",
            "open_issues_count": "open_issues_count",
            "open_pull_requests_count": "open_pull_requests_count",
            "pull_request_last_created_at": "pull_request_last_created_at",
            "recent_releases_count": "recent_releases_count",
            "stars_count": "stars_count",
            "total_issues_count": "issues_count",
            "total_pull_requests_count": "pull_requests_count",
            "total_releases_count": "releases_count",
            "unanswered_issues_count": "unanswered_issues_count",
            "unassigned_issues_count": "unassigned_issues_count",
        }
        for project in projects:
            metrics = ProjectHealthMetrics.objects.get_or_create(project=project)[0]

            # Update metrics based on requirements
            # TODO(ahmedxgouda): add these properties to the Project model
            # TODO(ahmedxgouda): open_pull_requests_count, total_issues_count,
            # TODO(ahmedxgouda): total_pull_requests_count,  recent_releases_count
            # TODO(ahmedxgouda): total_releases_count, last_released_at, last_committed_at
            # TODO(ahmedxgouda): update from owasp page: owasp_page_last_updated_at
            # TODO(ahmedxgouda): add score
            # TODO(ahmedxgouda): update is_funding_requirements_compliant,
            # TODO(ahmedxgouda): is_project_leaders_requirements_compliant
            for field, metric_field in field_mappings.items():
                value = getattr(project, field, 0)
                setattr(metrics, metric_field, value)

        self.stdout.write(self.style.SUCCESS("Project health metrics updated successfully."))
