"""A command to update OWASP chapters from owasp.org data."""

import logging
import time

from django.core.management.base import BaseCommand
from github.GithubException import UnknownObjectException

from apps.github.auth import get_github_client
from apps.github.utils import normalize_url
from apps.owasp.models.chapter import Chapter

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Scrape owasp.org pages and update relevant chapters."

    def add_arguments(self, parser) -> None:
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument("--offset", default=0, required=False, type=int)

    def handle(self, *args, **options) -> None:
        """Handle the command execution."""
        gh = get_github_client()

        active_chapters = Chapter.active_chapters.order_by("-created_at")
        active_chapters_count = active_chapters.count()
        offset = options["offset"]
        chapters = []
        for idx, chapter in enumerate(active_chapters[offset:]):
            prefix = f"{idx + offset + 1} of {active_chapters_count}"
            print(f"{prefix:<10} {chapter.owasp_url}")

            try:
                gh.get_repo(f"owasp/{chapter.key}")
            except UnknownObjectException:
                chapter.deactivate()
                continue

            chapter.leaders_raw = chapter.get_leaders()
            if leaders_emails := chapter.get_leaders_emails():
                chapter.sync_leaders(leaders_emails)

            # Get related URLs.
            scraped_urls = sorted(
                {
                    repository_url
                    for url in set(chapter.get_urls())
                    if (
                        repository_url := normalize_url(
                            chapter.get_related_url(
                                url, exclude_domains=("github.com", "owasp.org")
                            )
                        )
                    )
                    and repository_url not in {chapter.github_url, chapter.owasp_url}
                }
            )

            invalid_urls = set()
            related_urls = set()
            for scraped_url in scraped_urls:
                verified_url = chapter.verify_url(scraped_url)
                if not verified_url:
                    invalid_urls.add(scraped_url)
                    continue

                if verified_url := chapter.get_related_url(
                    normalize_url(verified_url, check_path=True)
                ):
                    related_urls.add(verified_url)
                else:
                    logger.info("Skipped related URL %s", verified_url)

            chapter.invalid_urls = sorted(invalid_urls)
            chapter.related_urls = sorted(related_urls)

            chapters.append(chapter)

            time.sleep(0.5)

        # Bulk save data.
        Chapter.bulk_save(chapters)
