"""A command to check OWASP project level compliance against the official source of truth."""

import logging
from urllib.request import urlopen

from django.core.management.base import BaseCommand

from apps.owasp.models.project import Project

logger = logging.getLogger(__name__)

# Official OWASP project levels source
PROJECT_LEVELS_URL = "https://raw.githubusercontent.com/OWASP/www-projectchapter-example/main/assets/project_levels.json"


class Command(BaseCommand):
    help = "Check OWASP project level compliance against official project_levels.json."

    def add_arguments(self, parser) -> None:
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Perform a dry run without updating the database.",
        )

    def fetch_official_project_levels(self) -> dict[str, str]:
        """Fetch and parse the official project levels JSON.

        Returns:
            dict: Mapping of project keys to their official levels.

        """
        try:
            with urlopen(PROJECT_LEVELS_URL, timeout=30) as response:  # noqa: S310
                import json

                data = json.loads(response.read().decode("utf-8"))
                if not data:
                    self.stdout.write(
                        self.style.ERROR("✗ Official project levels are unexpectedly empty")
                    )
                    logger.error(
                        "Official project levels returned empty data from %s", PROJECT_LEVELS_URL
                    )
                    return {}
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Fetched {len(data)} project levels from official source"
                    )
                )
                return data
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Failed to fetch project levels: {e}"))
            logger.exception("Failed to fetch project levels from %s", PROJECT_LEVELS_URL)
            return {}

    def normalize_level(self, level: str) -> str:
        """Normalize a level string to match ProjectLevel enum values.

        Args:
            level: The level string to normalize.

        Returns:
            str: Normalized level string.

        """
        level_mapping = {
            "incubator": "incubator",
            "lab": "lab",
            "production": "production",
            "flagship": "flagship",
            "labs": "lab",  # Handle plural form
            "incubators": "incubator",  # Handle plural form
            "flagships": "flagship",  # Handle plural form
        }
        normalized = level.lower().strip()
        return level_mapping.get(normalized, "other")

    def handle(self, *args, **options) -> None:
        """Handle the command execution."""
        dry_run = options["dry_run"]

        self.stdout.write(self.style.WARNING("Starting project level compliance check..."))

        if dry_run:
            self.stdout.write(self.style.NOTICE("🔍 DRY RUN MODE - No changes will be saved"))

        # Fetch official project levels
        official_levels = self.fetch_official_project_levels()
        if not official_levels:
            self.stdout.write(
                self.style.ERROR("✗ Could not fetch official project levels. Aborting.")
            )
            return

        # Get all active projects
        projects = Project.active_projects.all()
        total_projects = projects.count()

        projects_to_update = []
        compliant_count = 0
        non_compliant_count = 0
        not_in_official_list_count = 0

        self.stdout.write(
            self.style.NOTICE(f"\n📊 Checking {total_projects} active projects...\n")
        )

        for project in projects:
            # Extract project key (remove 'www-project-' prefix if present)
            project_key = project.key.replace("www-project-", "").lower()

            # Check if project exists in official list
            if project_key not in official_levels:
                # Project not in official list - mark as non-compliant
                if project.is_level_compliant:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠ {project.name} ({project.key}): Not found in official list"
                        )
                    )
                    project.is_level_compliant = False
                    projects_to_update.append(project)
                    non_compliant_count += 1
                else:
                    non_compliant_count += 1
                not_in_official_list_count += 1
                continue

            # Get official level and normalize it
            official_level = self.normalize_level(official_levels[project_key])
            local_level = project.level.lower()

            # Compare levels
            if official_level != local_level:
                # Levels don't match - mark as non-compliant
                if project.is_level_compliant:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠ {project.name} ({project.key}): "
                            f"Level mismatch - Local: {local_level}, Official: {official_level}"
                        )
                    )
                    logger.warning(
                        "Level mismatch for project %s: local=%s, official=%s",
                        project.key,
                        local_level,
                        official_level,
                    )
                    project.is_level_compliant = False
                    projects_to_update.append(project)
                    non_compliant_count += 1
                else:
                    non_compliant_count += 1
            else:
                # Levels match - mark as compliant
                if not project.is_level_compliant:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ {project.name} ({project.key}): Now compliant ({local_level})"
                        )
                    )
                    project.is_level_compliant = True
                    projects_to_update.append(project)
                compliant_count += 1

        # Update database
        if projects_to_update and not dry_run:
            Project.bulk_save(projects_to_update, fields=["is_level_compliant"])
            self.stdout.write(
                self.style.SUCCESS(f"\n✓ Updated {len(projects_to_update)} projects in database")
            )
        elif projects_to_update and dry_run:
            self.stdout.write(
                self.style.NOTICE(
                    f"\n🔍 Would update {len(projects_to_update)} projects (dry run)"
                )
            )

        # Print summary
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("\n📈 COMPLIANCE SUMMARY:\n"))
        self.stdout.write(f"  Total Projects:                {total_projects}")
        self.stdout.write(self.style.SUCCESS(f"  ✓ Compliant:                  {compliant_count}"))
        self.stdout.write(
            self.style.WARNING(f"  ⚠ Non-Compliant:             {non_compliant_count}")
        )
        self.stdout.write(
            self.style.ERROR(f"    - Not in official list:    {not_in_official_list_count}")
        )
        mismatch_count = non_compliant_count - not_in_official_list_count
        self.stdout.write(self.style.ERROR(f"    - Level mismatch:          {mismatch_count}"))
        self.stdout.write(f"  Changes Applied:               {len(projects_to_update)}")
        self.stdout.write("=" * 70 + "\n")

        if non_compliant_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠ {non_compliant_count} non-compliant projects detected. "
                    "These projects will receive a score penalty."
                )
            )

        self.stdout.write(self.style.SUCCESS("\n✓ Project level compliance check completed."))
