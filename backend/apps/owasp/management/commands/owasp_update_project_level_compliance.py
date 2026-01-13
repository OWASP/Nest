"""A command to detect non-compliant OWASP project levels."""

import logging
import re
from decimal import Decimal, InvalidOperation

import requests
from django.core.management.base import BaseCommand

from apps.owasp.models import ProjectHealthMetrics
from apps.owasp.utils.project_level import map_level

logger = logging.getLogger(__name__)

LEVELS_URL = (
    "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/project_levels.json"
)


def clean_name(name: str) -> str:
    """Normalize project names for matching with OWASP official data."""
    name = name.lower().replace("owasp", "")
    return re.sub(r"[^a-z0-9]+", "", name)


class Command(BaseCommand):
    help = "Update project level compliance."

    def handle(self, *args, **options):
        self.stdout.write("Updating project level compliance...")

        response = requests.get(LEVELS_URL, timeout=15)
        response.raise_for_status()

        official = response.json()

        by_repo: dict[str, Decimal] = {}
        by_name: dict[str, Decimal] = {}

        for item in official:
            raw_level = item.get("level")
            try:
                level = Decimal(str(raw_level))
            except (InvalidOperation, TypeError, ValueError):
                logger.debug("Skipping invalid project level: %s", raw_level)
                continue

            repo = item.get("repo")
            if repo:
                by_repo[repo.lower()] = level

            name = item.get("name")
            if name:
                by_name[clean_name(name)] = level

        metrics = ProjectHealthMetrics.objects.select_related("project")

        updated_metrics = []

        for metric in metrics:
            project = metric.project

            official_level = None
            if project.repo_url:
                slug = project.repo_url.rstrip("/").split("/")[-1].lower()
                official_level = by_repo.get(slug)

            if official_level is None:
                official_level = by_name.get(clean_name(project.name))

            if official_level is None:
                continue

            expected_level = map_level(official_level)
            if expected_level is None:
                continue

            metric.level_non_compliant = project.level != expected_level
            if metric.level_non_compliant:
                self.stdout.write(
                    self.style.WARNING(
                        f"Level mismatch: {project.name} "
                        f"local={project.level} "
                        f"official={expected_level}"
                    )
                )

            updated_metrics.append(metric)

        if updated_metrics:
            ProjectHealthMetrics.bulk_save(
                updated_metrics,
                fields=["level_non_compliant"],
            )

        self.stdout.write(f"Project level compliance updated for {len(updated_metrics)} metrics.")
