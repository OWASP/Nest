"""A command to set thresholds of OWASP project health requirements."""

from django.core.management.base import BaseCommand

from apps.owasp.models.project import Project
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements


class Command(BaseCommand):
    help = "Update or create health requirements for different project levels."

    level_requirements = {
        Project.ProjectLevel.FLAGSHIP: {
            "contributors_count": 5,
            "age_days": 30,
            "forks_count": 10,
            "last_commit_days": 180,
            "last_release_days": 365,
            "open_issues_count": 5,
            "open_pull_requests_count": 3,
            "owasp_page_last_update_days": 30,
            "last_pull_request_days": 30,
            "recent_releases_count": 2,
            "recent_releases_time_window_days": 90,
            "stars_count": 50,
            "total_pull_requests_count": 20,
            "total_releases_count": 5,
            "unanswered_issues_count": 3,
            "unassigned_issues_count": 3,
        },
        Project.ProjectLevel.INCUBATOR: {
            "contributors_count": 1,
            "age_days": 15,
            "forks_count": 2,
            "last_commit_days": 365,
            "last_release_days": 365,
            "open_issues_count": 10,
            "open_pull_requests_count": 5,
            "owasp_page_last_update_days": 60,
            "last_pull_request_days": 60,
            "recent_releases_count": 1,
            "recent_releases_time_window_days": 120,
            "stars_count": 10,
            "total_pull_requests_count": 5,
            "total_releases_count": 2,
            "unanswered_issues_count": 5,
            "unassigned_issues_count": 5,
        },
        Project.ProjectLevel.LAB: {
            "contributors_count": 3,
            "age_days": 20,
            "forks_count": 5,
            "last_commit_days": 270,
            "last_release_days": 365,
            "open_issues_count": 8,
            "open_pull_requests_count": 4,
            "owasp_page_last_update_days": 45,
            "last_pull_request_days": 45,
            "recent_releases_count": 1,
            "recent_releases_time_window_days": 90,
            "stars_count": 25,
            "total_pull_requests_count": 10,
            "total_releases_count": 3,
            "unanswered_issues_count": 4,
            "unassigned_issues_count": 4,
        },
        Project.ProjectLevel.OTHER: {
            "contributors_count": 2,
            "age_days": 10,
            "forks_count": 3,
            "last_commit_days": 365,
            "last_release_days": 730,
            "open_issues_count": 15,
            "open_pull_requests_count": 7,
            "owasp_page_last_update_days": 90,
            "last_pull_request_days": 90,
            "recent_releases_count": 0,
            "recent_releases_time_window_days": 180,
            "stars_count": 5,
            "total_pull_requests_count": 2,
            "total_releases_count": 1,
            "unanswered_issues_count": 10,
            "unassigned_issues_count": 10,
        },
        Project.ProjectLevel.PRODUCTION: {
            "contributors_count": 4,
            "age_days": 30,
            "forks_count": 7,
            "last_commit_days": 90,
            "last_release_days": 180,
            "open_issues_count": 5,
            "open_pull_requests_count": 3,
            "owasp_page_last_update_days": 30,
            "last_pull_request_days": 30,
            "recent_releases_count": 2,
            "recent_releases_time_window_days": 60,
            "stars_count": 40,
            "total_pull_requests_count": 15,
            "total_releases_count": 4,
            "unanswered_issues_count": 2,
            "unassigned_issues_count": 2,
        },
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--level",
            type=str,
            choices=[level[0] for level in Project.ProjectLevel.choices],
            help="Project level to update requirements for",
        )

    def get_level_requirements(self, level):
        """Get default requirements based on project level."""
        defaults = {
            "contributors_count": 1,
            "age_days": 0,
            "forks_count": 0,
            "last_release_days": 0,
            "last_commit_days": 1,
            "open_issues_count": 0,
            "open_pull_requests_count": 0,
            "owasp_page_last_update_days": 0,
            "last_pull_request_days": 0,
            "recent_releases_count": 0,
            "recent_releases_time_window_days": 0,
            "stars_count": 0,
            "total_pull_requests_count": 0,
            "total_releases_count": 0,
            "unanswered_issues_count": 0,
            "unassigned_issues_count": 0,
        }

        defaults.update(self.level_requirements.get(level, {}))
        return defaults

    def handle(self, *args, **options):
        level = options.get("level")

        if level:
            defaults = self.get_level_requirements(level)
            requirements, created = ProjectHealthRequirements.objects.get_or_create(
                level=level, defaults=defaults
            )

            action = "Created" if created else "Updated"
            print(f"{action} health requirements for {requirements.get_level_display()} projects")
        else:
            for level_choice in Project.ProjectLevel.choices:
                level_code = level_choice[0]
                defaults = self.get_level_requirements(level_code)

                requirements, created = ProjectHealthRequirements.objects.get_or_create(
                    level=level_code, defaults=defaults
                )

                if created:
                    print(f"Created default health requirements for {level_choice[1]} projects")
                else:
                    print(f"Health requirements already exist for {level_choice[1]} projects")
