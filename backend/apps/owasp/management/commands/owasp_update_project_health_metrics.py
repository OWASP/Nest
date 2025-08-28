"""A command to update OWASP project health metrics."""

import logging

import requests
from django.core.management.base import BaseCommand
from requests.exceptions import RequestException

from apps.owasp.models.project import Project
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics

logger = logging.getLogger(__name__)

OWASP_PROJECT_LEVELS_URL = (
    "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/project_levels.json"
)


class Command(BaseCommand):
    help = "Update OWASP project health metrics."

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--skip-official-levels",
            action="store_true",
            help="Skip fetching official project levels from OWASP GitHub repository",
        )
        parser.add_argument(
            "--sync-official-levels-only",
            action="store_true",
            help="Only sync official project levels, skip health metrics updates",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=30,
            help="HTTP timeout for fetching project levels (default: 30 seconds)",
        )

    def fetch_official_project_levels(self, timeout: int = 30) -> dict[str, str] | None:
        """Fetch project levels from OWASP GitHub repository.

        Args:
            timeout: HTTP request timeout in seconds

        Returns:
            Dict mapping project names to their official levels, or None if fetch fails

        """
        try:
            response = requests.get(
                OWASP_PROJECT_LEVELS_URL,
                timeout=timeout,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list):
                logger.exception(
                    "Invalid project levels data format",
                    extra={"expected": "list", "got": type(data).__name__},
                )
                return None

            # Convert the list to a dict mapping project names to their levels
            project_levels = {}
            for entry in data:
                if not isinstance(entry, dict):
                    continue
                project_name = entry.get("name")
                level = entry.get("level")
                if (
                    isinstance(project_name, str)
                    and isinstance(level, (str, int, float))
                    and project_name.strip()
                ):
                    project_levels[project_name.strip()] = str(level)

        except (RequestException, ValueError) as e:
            logger.exception(
                "Failed to fetch project levels",
                extra={"url": OWASP_PROJECT_LEVELS_URL, "error": str(e)},
            )
            return None
        else:
            return project_levels

    def update_official_levels(self, official_levels: dict[str, str]) -> int:
        """Update official levels for projects.

        Args:
            official_levels: Dict mapping project names to their official levels

        Returns:
            Number of projects updated

        """
        updated_count = 0
        projects_to_update = []

        # Normalize official levels by stripping whitespace and normalizing case
        normalized_official_levels = {
            k.strip().lower(): v.strip().lower() for k, v in official_levels.items()
        }

        for project in Project.objects.filter(is_active=True):
            normalized_project_name = project.name.strip().lower()
            if normalized_project_name in normalized_official_levels:
                official_level = normalized_official_levels[normalized_project_name]
                # Map string levels to enum values
                level_mapping = {
                    "incubator": "incubator",
                    "lab": "lab",
                    "production": "production",
                    "flagship": "flagship",
                    "2": "incubator",
                    "3": "lab",
                    "3.5": "production",
                    "4": "flagship",
                }
                mapped_level = level_mapping.get(official_level, "other")

                if project.project_level_official != mapped_level:
                    project.project_level_official = mapped_level
                    projects_to_update.append(project)
                    updated_count += 1

        if projects_to_update:
            Project.bulk_save(projects_to_update, fields=["project_level_official"])
            self.stdout.write(f"Updated official levels for {updated_count} projects")
        else:
            self.stdout.write("No official level updates needed")

        return updated_count

    def handle(self, *args, **options):
        skip_official_levels = options["skip_official_levels"]
        sync_official_levels_only = options["sync_official_levels_only"]
        timeout = options["timeout"]

        # Part 1: Sync official project levels during project sync
        if not skip_official_levels:
            self.stdout.write("Fetching official project levels from OWASP GitHub repository...")
            official_levels = self.fetch_official_project_levels(timeout=timeout)
            if official_levels:
                success_msg = (
                    f"Successfully fetched {len(official_levels)} official project levels"
                )
                self.stdout.write(success_msg)
                self.update_official_levels(official_levels)
            else:
                warning_msg = "Failed to fetch official project levels, continuing without updates"
                self.stdout.write(self.style.WARNING(warning_msg))

        # If only syncing official levels, stop here (Part 1 only)
        if sync_official_levels_only:
            self.stdout.write(self.style.SUCCESS("Official level sync completed."))
            return

        # Part 2: Update project health metrics (only if not sync-only mode)
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
        for project in Project.objects.filter(is_active=True):
            self.stdout.write(self.style.NOTICE(f"Evaluating metrics for project: {project.name}"))
            metrics = ProjectHealthMetrics(project=project)

            # Update metrics based on requirements.
            for metric_field, project_field in metric_project_field_mapping.items():
                setattr(metrics, metric_field, getattr(project, project_field))

            project_health_metrics.append(metrics)

        ProjectHealthMetrics.bulk_save(project_health_metrics)
        self.stdout.write(self.style.SUCCESS("Evaluated projects health metrics successfully. "))
