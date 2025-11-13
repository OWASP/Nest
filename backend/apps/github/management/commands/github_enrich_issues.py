"""A command to update OWASP entities related repositories data."""

import logging

from django.core.management.base import BaseCommand

from apps.common.open_ai import OpenAi
from apps.github.models.issue import Issue

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Enrich GitHub issue with AI generated data."

    def add_arguments(self, parser) -> None:
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument("--offset", default=0, required=False, type=int)
        parser.add_argument(
            "--force-update-hint", default=False, required=False, action="store_true"
        )
        parser.add_argument(
            "--force-update-summary", default=False, required=False, action="store_true"
        )
        parser.add_argument("--update-hint", default=True, required=False, action="store_true")
        parser.add_argument("--update-summary", default=True, required=False, action="store_true")

    def handle(self, *args, **options) -> None:
        """Handle the command execution.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        force_update_hint = options["force_update_hint"]
        force_update_summary = options["force_update_summary"]
        offset = options["offset"]

        is_force_update = any((force_update_hint, force_update_summary))
        open_issues = (
            Issue.open_issues if is_force_update else Issue.open_issues.without_summary
        ).order_by("-created_at")
        open_issues_count = open_issues.count()

        issues = []
        open_ai = OpenAi()
        update_fields = []
        update_fields += ["hint"] if (update_hint := options["update_hint"]) else []
        update_fields += ["summary"] if (update_summary := options["update_summary"]) else []
        for idx, issue in enumerate(open_issues[offset:]):
            prefix = f"{idx + offset + 1} of {open_issues_count - offset}"
            print(f"{prefix:<10} {issue.title}")

            if update_hint:
                issue.generate_hint(open_ai=open_ai)

            if update_summary:
                issue.generate_summary(open_ai=open_ai)

            issues.append(issue)

        Issue.bulk_save(issues, fields=update_fields)
