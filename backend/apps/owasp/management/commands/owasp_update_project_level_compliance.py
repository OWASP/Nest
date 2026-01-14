"""Update OWASP project level compliance status.

This command compares locally stored project levels against
official OWASP project classification data and determines
whether each project is level-compliant.

Projects whose locally assigned level does not match the
official OWASP classification are flagged as non-compliant.
This compliance flag is later used during health score
calculation to apply penalties where appropriate.
"""

import re
from decimal import Decimal, InvalidOperation

import requests
from django.core.management.base import BaseCommand

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics
from apps.owasp.utils.project_level import map_level

LEVELS_URL = (
    "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/project_levels.json"
)


def normalize_name(name: str) -> str:
    """Normalize project names for comparison."""
    return re.sub(r"[^a-z0-9]+", "", name.lower().replace("owasp", ""))


class Command(BaseCommand):
    """Detect and persist OWASP project level compliance.

    This command fetches official OWASP project level data,
    maps it to the internal ProjectLevel enum, and updates
    project health metrics to indicate whether a project's
    stored level matches the official classification.
    """

    help = "Detect and flag OWASP project level non-compliance."

    def handle(self, *args, **options) -> None:
        """Execute project level compliance detection.

        For each project health metric entry, this method
        determines the expected project level based on
        official OWASP data and marks the project as
        level non-compliant when a mismatch is detected.
        """
        try:
             response = requests.get(LEVELS_URL, timeout=15)
             response.raise_for_status()
             official_data = response.json()
         except requests.RequestException as exc:
             self.stdout.write(
                 self.style.ERROR(f"Failed to fetch official project levels: {exc}")
             )
             return

        by_repo: dict[str, Decimal] = {}
        by_name: dict[str, Decimal] = {}

        for item in official_data:
            raw_level = item.get("level")
            try:
                level = Decimal(str(raw_level))
            except (InvalidOperation, TypeError, ValueError):
                continue

            if repo := item.get("repo"):
                by_repo[repo.lower()] = level

            if name := item.get("name"):
                by_name[normalize_name(name)] = level

        metrics = ProjectHealthMetrics.get_latest_health_metrics().select_related("project")
        updated_metrics = []

        for metric in metrics:
            project = metric.project
            official_level = None

            if project.owasp_url:
                slug = project.owasp_url.rstrip("/").split("/")[-1].lower()
                official_level = by_repo.get(slug)

            if official_level is None:
                official_level = by_name.get(normalize_name(project.name))

            if official_level is None:
                continue

            expected_level = map_level(official_level)
            if expected_level is None:
                continue

            metric.level_non_compliant = project.level != expected_level
            updated_metrics.append(metric)

        if updated_metrics:
            ProjectHealthMetrics.bulk_save(
                updated_metrics,
                fields=["level_non_compliant"],
            )

        self.stdout.write(
            self.style.SUCCESS(f"Updated level compliance for {len(updated_metrics)} projects.")
        )
