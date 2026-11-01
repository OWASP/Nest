"""A command to update OWASP committees from owasp.org data."""

import logging
import time

from django.core.management.base import BaseCommand

from apps.github.utils import normalize_url
from apps.owasp.models.committee import Committee
from apps.owasp.sync import OwaspSync

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync OWASP committees from owasp.org."

    def add_arguments(self, parser) -> None:
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument("--offset", default=0, required=False, type=int)

    def handle(self, *args, **options) -> None:
        """Handle the command execution."""
        active_committees = Committee.active_committees.order_by("-created_at")
        active_committees_count = active_committees.count()
        offset = options["offset"]
        committees = []
        for idx, committee in enumerate(active_committees[offset:]):
            prefix = f"{idx + offset + 1} of {active_committees_count}"
            page_url = OwaspSync.page_url("committee", committee.nest_key)
            self.stdout.write(f"{prefix:<10} {page_url}\n")

            sync = OwaspSync(page_url)
            if sync.page_tree is None:
                if not sync.is_request_failed:
                    committee.deactivate()
                continue

            OwaspSync.apply_leaders(committee, sync.get_leaders())

            # Get related URLs from the committee page.
            found_urls = sorted(
                {
                    repository_url
                    for url in sync.get_urls()
                    if (
                        repository_url := normalize_url(
                            committee.get_related_url(
                                url, exclude_domains=("github.com", "owasp.org")
                            )
                        )
                    )
                    and repository_url not in {committee.github_url, committee.owasp_url}
                }
            )
            if not found_urls:
                committees.append(committee)
                time.sleep(0.5)
                continue

            invalid_urls = set()
            related_urls = set()
            for found_url in found_urls:
                verified_url = sync.verify_url(found_url)
                if not verified_url:
                    invalid_urls.add(found_url)
                    continue

                if verified_url := committee.get_related_url(
                    normalize_url(verified_url, check_path=True)
                ):
                    related_urls.add(verified_url)
                else:
                    logger.info("Skipped related URL %s", verified_url)

            committee.invalid_urls = sorted(invalid_urls)
            committee.related_urls = sorted(related_urls)

            committees.append(committee)

            time.sleep(0.5)

        # Bulk save data.
        Committee.bulk_save(committees)
