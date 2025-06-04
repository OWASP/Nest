"""A command to update OWASP project health metrics."""

from django.core.management.base import BaseCommand

from apps.owasp.models.project import Project
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics

MINIMUM_LEADERS = 3


class Command(BaseCommand):
    help = "Update OWASP project health metrics."

    def handle(self, *args, **options):
        projects = Project.objects.all()
        field_mappings = {
            "contributors_count": "contributors_count",
            "created_at": "created_at",
            "forks_count": "forks_count",
            "is_funding_requirements_compliant": "is_funding_requirements_compliant",
            "last_released_at": "released_at",
            "last_committed_at": "pushed_at",
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
        updated_count = errors_count = 0
        for project in projects:
            try:
                self.stdout.write(
                    self.style.NOTICE(f"Updating metrics for project: {project.name}")
                )
                metrics = ProjectHealthMetrics.objects.get_or_create(project=project)[0]

                # Update metrics based on requirements
                # TODO(ahmedxgouda): update from owasp page: owasp_page_last_updated_at
                # TODO(ahmedxgouda): add score
                for metric_field, project_field in field_mappings.items():
                    value = getattr(project, project_field)
                    setattr(metrics, metric_field, value)

                is_leaders_compliant = project.leaders_count >= MINIMUM_LEADERS
                metrics.is_project_leaders_requirements_compliant = is_leaders_compliant
                metrics.save()
                updated_count += 1
            except (AttributeError, ValueError, TypeError):
                self.stdout.write(self.style.ERROR(f"Error updating project {project.name}"))
                errors_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {updated_count} projects health metrics successfully. "
                f"Encountered errors for {errors_count} projects."
            )
        )
