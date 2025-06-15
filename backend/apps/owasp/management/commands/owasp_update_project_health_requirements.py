"""A command to set thresholds of OWASP project health requirements."""

from django.core.management.base import BaseCommand

from apps.owasp.models.project import Project
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements


class Command(BaseCommand):
    help = "Set project health requirements for each level."

    LEVEL_REQUIREMENTS = {
        Project.ProjectLevel.INCUBATOR: {
            "age_days": 15,
            "contributors_count": 1,
            "forks_count": 2,
            "is_funding_requirements_compliant": True,
            "is_leader_requirements_compliant": False,
            "last_commit_days": 365,
            "last_pull_request_days": 60,
            "last_release_days": 365,
            "open_issues_count": 10,
            "open_pull_requests_count": 5,
            "owasp_page_last_update_days": 60,
            "recent_releases_count": 1,
            "recent_releases_time_window_days": 120,
            "stars_count": 10,
            "total_pull_requests_count": 5,
            "total_releases_count": 2,
            "unanswered_issues_count": 5,
            "unassigned_issues_count": 5,
        },
        Project.ProjectLevel.LAB: {
            "age_days": 20,
            "contributors_count": 3,
            "forks_count": 5,
            "is_funding_requirements_compliant": True,
            "is_leader_requirements_compliant": True,
            "last_commit_days": 270,
            "last_pull_request_days": 45,
            "last_release_days": 365,
            "open_issues_count": 8,
            "open_pull_requests_count": 4,
            "owasp_page_last_update_days": 45,
            "recent_releases_count": 1,
            "recent_releases_time_window_days": 90,
            "stars_count": 25,
            "total_pull_requests_count": 10,
            "total_releases_count": 3,
            "unanswered_issues_count": 4,
            "unassigned_issues_count": 4,
        },
        Project.ProjectLevel.PRODUCTION: {
            "age_days": 30,
            "contributors_count": 4,
            "forks_count": 7,
            "is_funding_requirements_compliant": True,
            "is_leader_requirements_compliant": True,
            "last_commit_days": 90,
            "last_pull_request_days": 30,
            "last_release_days": 180,
            "open_issues_count": 5,
            "open_pull_requests_count": 3,
            "owasp_page_last_update_days": 30,
            "recent_releases_count": 2,
            "recent_releases_time_window_days": 60,
            "stars_count": 40,
            "total_pull_requests_count": 15,
            "total_releases_count": 4,
            "unanswered_issues_count": 2,
            "unassigned_issues_count": 2,
        },
        Project.ProjectLevel.FLAGSHIP: {
            "age_days": 30,
            "contributors_count": 5,
            "forks_count": 10,
            "is_funding_requirements_compliant": True,
            "is_leader_requirements_compliant": True,
            "last_commit_days": 180,
            "last_pull_request_days": 30,
            "last_release_days": 365,
            "open_issues_count": 5,
            "open_pull_requests_count": 3,
            "owasp_page_last_update_days": 30,
            "recent_releases_count": 2,
            "recent_releases_time_window_days": 90,
            "stars_count": 50,
            "total_pull_requests_count": 20,
            "total_releases_count": 5,
            "unanswered_issues_count": 3,
            "unassigned_issues_count": 3,
        },
    }

    def get_level_requirements(self, level):
        """Get default requirements based on project level."""
        return self.LEVEL_REQUIREMENTS.get(
            level,
            {
                "age_days": 0,
                "contributors_count": 0,
                "forks_count": 0,
                "is_funding_requirements_compliant": True,
                "is_leader_requirements_compliant": True,
                "last_commit_days": 0,
                "last_pull_request_days": 0,
                "last_release_days": 0,
                "open_issues_count": 0,
                "open_pull_requests_count": 0,
                "owasp_page_last_update_days": 0,
                "recent_releases_count": 0,
                "recent_releases_time_window_days": 0,
                "stars_count": 0,
                "total_pull_requests_count": 0,
                "total_releases_count": 0,
                "unanswered_issues_count": 0,
                "unassigned_issues_count": 0,
            },
        )

    def handle(self, *args, **options) -> None:
        """Handle the command execution."""
        for level_code, level_name in sorted(Project.ProjectLevel.choices):
            _, created = ProjectHealthRequirements.objects.update_or_create(
                level=level_code,
                defaults=self.get_level_requirements(level_code),
            )

            print(
                f"{'Created' if created else 'Updated'} health requirements for "
                f"{level_name} projects"
            )
