"""A command to update OWASP committees from owasp.org data."""

import logging
import time

from django.core.management.base import BaseCommand
from github.GithubException import UnknownObjectException

from apps.github.auth import get_github_client
from apps.github.utils import normalize_url
from apps.owasp.models.committee import Committee

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Scrape owasp.org pages and update relevant committees."

    def add_arguments(self, parser) -> None:
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument("--offset", default=0, required=False, type=int)

    def handle(self, *args, **options) -> None:
        """Handle the command execution."""
        gh = get_github_client()

        active_committees = Committee.active_committees.order_by("-created_at")
        active_committees_count = active_committees.count()
        offset = options["offset"]
        committees = []
        for idx, committee in enumerate(active_committees[offset:]):
            prefix = f"{idx + offset + 1} of {active_committees_count}"
            print(f"{prefix:<10} {committee.owasp_url}")

            try:
                gh.get_repo(f"owasp/{committee.key}")
            except UnknownObjectException:
                committee.deactivate()
                continue

            committee.leaders_raw = committee.get_leaders()
            if leaders_emails := committee.get_leaders_emails():
                committee.sync_leaders(leaders_emails)

            # Get related URLs.
            scraped_urls = sorted(
                {
                    repository_url
                    for url in set(committee.get_urls())
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

            invalid_urls = set()
            related_urls = set()
            for scraped_url in scraped_urls:
                verified_url = committee.verify_url(scraped_url)
                if not verified_url:
                    invalid_urls.add(scraped_url)
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
