"""A command to update OWASP projects related repositories data."""

import logging

from django.core.management.base import BaseCommand

from apps.common.open_ai import OpenAi
from apps.core.models.prompt import Prompt
from apps.owasp.models.project import Project

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Enrich OWASP projects with AI generated data."

    def add_arguments(self, parser) -> None:
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument("--offset", default=0, required=False, type=int)
        parser.add_argument(
            "--force-update-summary", default=False, required=False, action="store_true"
        )
        parser.add_argument("--update-summary", default=True, required=False, action="store_true")

    def handle(self, *args, **options) -> None:
        """Execute the enrichment process for OWASP projects."""
        open_ai = OpenAi()

        force_update_summary = options["force_update_summary"]
        is_force_update = force_update_summary

        active_projects = (
            Project.active_projects if is_force_update else Project.active_projects.without_summary
        ).order_by("-created_at")
        active_projects_count = active_projects.count()

        update_summary = options["update_summary"]
        update_fields = []
        update_fields += ["summary"] if update_summary else []

        projects = []
        offset = options["offset"]
        for idx, project in enumerate(active_projects[offset:]):
            prefix = f"{idx + offset + 1} of {active_projects_count - offset}"
            self.stdout.write(f"{prefix:<10} {project.owasp_url}\n")

            # Generate summary
            if update_summary and (prompt := Prompt.get_owasp_project_summary()):
                project.generate_summary(prompt=prompt, open_ai=open_ai)

            projects.append(project)

        Project.bulk_save(projects, fields=update_fields)
