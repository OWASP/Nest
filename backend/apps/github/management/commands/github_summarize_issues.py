"""A command to update OWASP entities related repositories data."""

import logging

from django.core.management.base import BaseCommand

from apps.common.open_ai import OpenAi
from apps.github.models import Issue

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

            open_ai.set_prompt(
                (
                    "Summarize the following GitHub issue using imperative mood."
                    "Add a good amount of technical details."
                    "Include possible first steps of tackling the problem."
                )
                if issue.project.is_code_type or issue.project.is_tool_type
                else (
                    "Summarize the following GitHub issue."
                    "Avoid mentioning author's name or issue creation date."
                    "Add a hint of what needs to be done if possible."
                )
            )

            issue.summary = open_ai.set_input(f"{issue.title}\r\n{issue.body}").complete() or ""
            issues.append(issue)

        # Bulk save data.
        Issue.bulk_save(issues, fields=("summary",))
