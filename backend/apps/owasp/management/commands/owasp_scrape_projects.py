"""A command to update OWASP projects from owasp.org data."""

import logging
import time

from django.core.management.base import BaseCommand
from github.GithubException import UnknownObjectException

from apps.github.auth import get_github_client
from apps.github.constants import GITHUB_USER_RE
from apps.github.utils import normalize_url
from apps.owasp.models.project import Project

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Scrape owasp.org pages and update relevant projects."

    def add_arguments(self, parser) -> None:
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument("--offset", default=0, required=False, type=int)

    def handle(self, *args, **options) -> None:
        """Handle the command execution.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.
                offset (int): The starting index for processing.

        """
        gh = get_github_client()

        active_projects = Project.active_projects.order_by("-created_at")
        active_projects_count = active_projects.count()
        offset = options["offset"]
        projects = []
        for idx, project in enumerate(active_projects[offset:]):
            prefix = f"{idx + offset + 1} of {active_projects_count}"
            print(f"{prefix:<10} {project.owasp_url}")

            try:
                gh.get_repo(f"owasp/{project.key}")
            except UnknownObjectException:
                project.deactivate()
                continue

            project.audience = project.get_audience()
            project.leaders_raw = project.get_leaders()
            if leaders_emails := project.get_leaders_emails():
                project.sync_leaders(leaders_emails)

            # Get GitHub URLs.
            scraped_urls = sorted(
                {
                    repository_url
                    for url in set(project.get_urls(domain="github.com"))
                    if (repository_url := normalize_url(project.get_related_url(url)))
                    and repository_url not in {project.github_url, project.owasp_url}
                }
            )

            invalid_urls: set[str] = set()
            related_urls: set[str] = set()
            for scraped_url in scraped_urls:
                verified_url = project.verify_url(scraped_url)
                if not verified_url:
                    invalid_urls.add(scraped_url)
                    continue

                verified_url = project.get_related_url(normalize_url(verified_url))
                if verified_url:
                    if GITHUB_USER_RE.match(verified_url):
                        try:
                            gh_organization = gh.get_organization(verified_url.split("/")[-1])
                            related_urls.update(
                                f"https://github.com/{gh_repository.full_name.lower()}"
                                for gh_repository in gh_organization.get_repos()
                            )
                        except UnknownObjectException:
                            logger.info(
                                "Couldn't get GitHub organization repositories for %s",
                                verified_url,
                            )
                    else:
                        related_urls.add(verified_url)
                else:
                    logger.info("Skipped related URL %s", verified_url)

            project.invalid_urls = sorted(invalid_urls)
            project.related_urls = sorted(related_urls)

            projects.append(project)

            time.sleep(0.5)

        # Bulk save data.
        Project.bulk_save(projects)
