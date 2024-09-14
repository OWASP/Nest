"""A command to update OWASP entities related repositories data."""

import logging

from django.core.management.base import BaseCommand

from apps.common.open_ai import OpenAi
from apps.github.models.issue import Issue

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Enriches GitHub issue with AI generated data."

    def add_arguments(self, parser):
        parser.add_argument("--offset", default=0, required=False, type=int)
        parser.add_argument("--update-hint", default=True, required=False, type=bool)
        parser.add_argument("--update-summary", default=True, required=False, type=bool)

    def handle(self, *args, **options):
        open_ai = OpenAi()
        open_issues = Issue.open_issues.without_summary.order_by("-created_at")
        open_issues_count = open_issues.count()

        update_hint = options["update_hint"]
        update_summary = options["update_summary"]
        update_fields = []
        update_fields += ["hint"] if update_hint else []
        update_fields += ["summary"] if update_summary else []

        issues = []
        offset = options["offset"]
        for idx, issue in enumerate(open_issues[offset:]):
            prefix = f"{idx + offset + 1} of {open_issues_count - offset}"
            print(f"{prefix:<10} {issue.title}")

            open_ai.set_input(f"{issue.title}\r\n{issue.body}")

            # Generate summary
            if update_summary:
                open_ai.set_max_tokens(500).set_prompt(
                    (
                        "Summarize the following GitHub issue."
                        "Avoid mentioning author's name or issue creation date."
                        "Avoid using lists for description."
                        "Do not use markdown in output."
                        "Limit summary by 3 sentences."
                    )
                    if issue.project.is_documentation_type
                    else (
                        "Summarize the following GitHub issue using imperative mood."
                        "Use a good amount technical details."
                        "Avoid using lists for description."
                        "Do not use mardown in output."
                        "Limit summary by 3 sentences."
                    )
                )
                issue.summary = open_ai.complete() or ""

            # Generate hint
            if update_hint:
                open_ai.set_max_tokens(1000).set_prompt(
                    "Describe possible steps of approaching the problem."
                    "Limit output by 10 steps."
                )
                issue.hint = open_ai.complete() or ""

            issues.append(issue)

        # Bulk save data.
        Issue.bulk_save(issues, fields=update_fields)
