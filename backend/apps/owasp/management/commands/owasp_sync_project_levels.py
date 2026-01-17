"""A command to sync OWASP project levels from official source and flag non-compliant projects."""

import json
import logging

from django.core.management.base import BaseCommand

from apps.github.utils import get_repository_file_content
from apps.owasp.models.project import Project

logger: logging.Logger = logging.getLogger(__name__)

PROJECT_LEVELS_URL = (
    "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/project_levels.json"
)


def normalize_level(value):
    """Normalize level value to float for comparison."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


class Command(BaseCommand):
    help = "Sync OWASP project levels from official source and flag non-compliant projects."

    def handle(self, *args, **options) -> None:
        """Handle the command execution."""
        self.stdout.write(
            self.style.NOTICE("Fetching project levels from OWASP GitHub repository...")
        )

        # Fetch project levels from official source
        project_levels_content = get_repository_file_content(PROJECT_LEVELS_URL)
        if not project_levels_content:
            self.stdout.write(
                self.style.ERROR("Failed to fetch project levels from OWASP GitHub repository.")
            )
            return

        try:
            official_project_levels = json.loads(project_levels_content)
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Failed to parse project levels JSON: {str(e)}"))
            return

        # Create a mapping of repo key to normalized official level
        # Note: -1 is treated as a valid official level (incubator / no level)
        official_levels_map = {}
        for project_data in official_project_levels:
            repo_key = project_data.get("repo")
            level = project_data.get("level")
            if repo_key and level is not None:
                normalized = normalize_level(level)
                if normalized is not None:
                    official_levels_map[repo_key] = normalized

        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded {len(official_levels_map)} official project levels from OWASP."
            )
        )

        # Compute coverage: which official projects are not in Nest
        official_keys = set(official_levels_map.keys())
        local_keys = set(Project.active_projects.values_list("key", flat=True))
        missing_locally = official_keys - local_keys
        self.stdout.write(
            self.style.NOTICE(
                f"{len(missing_locally)} official OWASP projects are not present in Nest (ignored)."
            )
        )

        # Determine new compliance status for each project
        projects_to_update = []
        changes_made = []

        for project in Project.active_projects.all():
            official_level = official_levels_map.get(project.key)

            # Determine if project should be marked as non-compliant
            # True = non-compliant, False = compliant
            if official_level is None:
                new_is_level_non_compliant = True
            else:
                local_level = normalize_level(project.level_raw)
                new_is_level_non_compliant = local_level != official_level

            # Only update if flag actually changed
            if project.is_level_non_compliant != new_is_level_non_compliant:
                # Create change record before mutation
                old_status = "compliant" if not project.is_level_non_compliant else "non-compliant"
                new_status = "compliant" if not new_is_level_non_compliant else "non-compliant"

                if new_is_level_non_compliant:
                    if official_level is None:
                        reason = "missing from official OWASP project_levels.json"
                    else:
                        local_level = normalize_level(project.level_raw)
                        reason = (
                            f"level mismatch (local: {local_level}, official: {official_level})"
                        )
                    changes_made.append(
                        {
                            "key": project.key,
                            "old": old_status,
                            "new": new_status,
                            "reason": reason,
                        }
                    )
                else:
                    changes_made.append(
                        {
                            "key": project.key,
                            "old": old_status,
                            "new": new_status,
                            "reason": "now compliant with official level",
                        }
                    )

                # Mutate and queue for update
                project.is_level_non_compliant = new_is_level_non_compliant
                projects_to_update.append(project)

        # Log results and update if necessary
        self.stdout.write(
            self.style.NOTICE(f"Total projects checked: {Project.active_projects.count()}")
        )

        if not projects_to_update:
            self.stdout.write(self.style.SUCCESS("No compliance status changes detected."))
            return

        # Log all changes
        for change in changes_made:
            if change["new"] == "non-compliant":
                logger.warning(f"Project {change['key']}: {change['reason']} → non-compliant")
                self.stdout.write(self.style.WARNING(f"  {change['key']}: {change['reason']}"))
            else:
                logger.info(f"Project {change['key']}: {change['reason']}")

        # Perform bulk update
        Project.objects.bulk_update(
            projects_to_update,
            ["is_level_non_compliant"],
            batch_size=1000,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Updated {len(projects_to_update)} compliance status records.")
        )
