"""A command to update OWASP entities related repositories data."""

import logging
import os

import github
from django.core.management.base import BaseCommand
from github.GithubException import UnknownObjectException

from apps.github.common import sync_repository
from apps.github.constants import GITHUB_ITEMS_PER_PAGE
from apps.github.utils import get_repository_path
from apps.owasp.models.project import Project

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to update OWASP project related repositories."""

    help = "Updates OWASP project related repositories."

    def add_arguments(self, parser):
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument("--offset", default=0, required=False, type=int)

    def handle(self, *args, **options):
        """Handle the command execution.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        active_projects = Project.active_projects.order_by("-created_at")
        active_projects_count = active_projects.count()
        gh = github.Github(os.getenv("GITHUB_TOKEN"), per_page=GITHUB_ITEMS_PER_PAGE)

        offset = options["offset"]
        projects = []
        for idx, project in enumerate(active_projects[offset:]):
            prefix = f"{idx + offset + 1} of {active_projects_count}"
            print(f"{prefix:<10} {project.owasp_url}")

            repository_urls = project.related_urls.copy()
            for repository_url in repository_urls:
                repository_path = get_repository_path(repository_url)
                if not repository_path:
                    logger.info("Couldn't get repository path for %s", repository_url)
                    continue

                try:
                    gh_repository = gh.get_repo(repository_path)
                except UnknownObjectException as e:
                    if e.data["status"] == "404" and "Not Found" in e.data["message"]:
                        project.invalid_urls.add(repository_url)
                        project.related_urls.remove(repository_url)
                        project.save(update_fields=("invalid_urls", "related_urls"))
                        continue

                organization, repository = sync_repository(gh_repository)
                if organization is not None:
                    organization.save()

                project.repositories.add(repository)

            projects.append(project)

        # Bulk save data.
        Project.bulk_save(projects)
