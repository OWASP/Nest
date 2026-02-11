"""A command to update OWASP committees related repositories data."""

import logging

from django.core.management.base import BaseCommand

from apps.common.open_ai import OpenAi
from apps.core.models.prompt import Prompt
from apps.owasp.models.committee import Committee

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Enrich OWASP committees with AI generated data."

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
        """Execute the enrichment process for OWASP committees."""
        open_ai = OpenAi()

        force_update_summary = options["force_update_summary"]
        is_force_update = force_update_summary

        active_committees = (
            Committee.active_committees
            if is_force_update
            else Committee.active_committees.without_summary
        ).order_by("-created_at")
        active_committees_count = active_committees.count()

        update_summary = options["update_summary"]
        update_fields = []
        update_fields += ["summary"] if update_summary else []

        committees = []
        offset = options["offset"]
        for idx, committee in enumerate(active_committees[offset:]):
            prefix = f"{idx + offset + 1} of {active_committees_count - offset}"
            self.stdout.write(f"{prefix:<10} {committee.owasp_url}")

            # Generate summary
            if update_summary and (prompt := Prompt.get_owasp_committee_summary()):
                committee.generate_summary(prompt=prompt, open_ai=open_ai)

            committees.append(committee)

        Committee.bulk_save(committees, fields=update_fields)
