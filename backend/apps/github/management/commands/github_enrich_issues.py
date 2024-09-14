"""A command to update OWASP entities related repositories data."""

import logging

from django.core.management.base import BaseCommand

from apps.common.open_ai import OpenAi
from apps.github.models.issue import Issue

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Populated GitHub issue summary."

    def add_arguments(self, parser):
        parser.add_argument("--offset", default=0, required=False, type=int)

    def handle(self, *args, **options):
        open_ai = OpenAi()
        open_issues = Issue.open_issues.without_summary.order_by("-created_at")
        open_issues_count = open_issues.count()

        issues = []
        offset = options["offset"]
        for idx, issue in enumerate(open_issues[offset:]):
            prefix = f"{idx + offset + 1} of {open_issues_count - offset}"
            print(f"{prefix:<10} {issue.title}")

            open_ai.set_input(f"{issue.title}\r\n{issue.body}")

            # Generate summary
            open_ai.set_max_tokens(500).set_prompt(
                (
                    "Summarize the following GitHub issue using imperative mood."
                    "Use a good amount technical details."
                    "Avoid using lists for description."
                    "Do not use mardown in output."
                )
                if issue.project.is_code_type or issue.project.is_tool_type
                else (
                    "Summarize the following GitHub issue."
                    "Avoid mentioning author's name or issue creation date."
                    "Avoid using lists for description."
                    "Do not use markdown in output."
                )
            )
            issue.summary = open_ai.complete() or ""

            # Generate hint
            open_ai.set_max_tokens(1000).set_prompt(
                "Describe possible first steps of approaching the problem."
            )
            issue.hint = open_ai.complete() or ""

            issues.append(issue)

        # Bulk save data.
        Issue.bulk_save(issues, fields=("hint", "summary"))
