from decimal import Decimal
import re
import requests

from django.core.management.base import BaseCommand

from apps.owasp.models import ProjectHealthMetrics
from apps.owasp.utils.project_level import map_level


LEVELS_URL = (
    "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/project_levels.json"
)


def clean_name(name: str) -> str:
    name = name.lower().replace("owasp", "")
    return re.sub(r"[^a-z0-9]+", "", name)


class Command(BaseCommand):
    help = "Update project level compliance"

    def handle(self, *args, **options):
        self.stdout.write("Updating project level compliance...")

        response = requests.get(LEVELS_URL, timeout=15)
        response.raise_for_status()

        official = response.json()

        by_repo = {}
        by_name = {}

        for item in official:
            try:
                level = Decimal(item.get("level"))
            except Exception:
                continue

            if item.get("repo"):
                by_repo[item["repo"].lower()] = level

            if item.get("name"):
                by_name[clean_name(item["name"])] = level

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

            expected = int(official_level)
            if expected is None:
                continue

            metric.level_non_compliant = project.level != expected
            updated_metrics.append(metric)

        if updated_metrics:
            ProjectHealthMetrics.bulk_save(
                updated_metrics,
                update_fields=["level_non_compliant"],
            )

        self.stdout.write(
            f"Project level compliance updated for {len(updated_metrics)} metrics."
        )
