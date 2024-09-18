"""A command to update OWASP entities related repositories data."""

import logging

import requests
from django.core.management.base import BaseCommand

from apps.common.open_ai import OpenAi
from apps.owasp.models.project import Project

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Enrich OWASP projects with AI generated data."

    def add_arguments(self, parser):
        parser.add_argument("--offset", default=0, required=False, type=int)
        parser.add_argument(
            "--force-update-summary", default=False, required=False, action="store_true"
        )
        parser.add_argument("--update-summary", default=True, required=False, action="store_true")

    def handle(self, *args, **options):
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
            print(f"{prefix:<10} {project.owasp_url}")

            open_ai.set_input(requests.get(project.raw_index_md_url, timeout=30).text)

            # Generate summary
            if update_summary:
                open_ai.set_max_tokens(500).set_prompt(
                    "Summarize the following OWASP project description using simple English."
                    "Make sure to mention project type."
                    "Do not use lists for description."
                    "Do not use markdown in output."
                    "Limit the entire summary to 5 sentences."
                )
                project.summary = open_ai.complete() or ""

            projects.append(project)

        Project.bulk_save(projects, fields=update_fields)
