"""A command to update OWASP related organizations."""

import logging
import os

import github
from django.core.management.base import BaseCommand
from github.GithubException import BadCredentialsException

from apps.core.utils.index import unregister_indexes
from apps.github.common import sync_repository
from apps.github.constants import GITHUB_ITEMS_PER_PAGE
from apps.github.models.organization import Organization

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Fetch external organizations and update relevant entities."""

    help = "Fetch external organizations and update relevant entities."

    def add_arguments(self, parser) -> None:
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument(
            "--organization",
            required=False,
            type=str,
            help="The organization name (e.g. juice-shop, DefectDojo')",
        )

    def handle(self, *_args, **options) -> None:
        """Handle the command execution.

        Args:
            *_args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        unregister_indexes()  # Disable automatic indexing

        try:
            gh = github.Github(os.getenv("GITHUB_TOKEN"), per_page=GITHUB_ITEMS_PER_PAGE)
        except BadCredentialsException:
            logger.warning(
                "Invalid GitHub token. Please create or update .env file with a valid token."
            )
            return

        organizations = Organization.related_organizations.all()
        if organization := options["organization"]:
            organizations = organizations.filter(login__iexact=organization)

        if not organizations.exists():
            logger.error("No OWASP related organizations found")
            return

        organizations_count = organizations.count()
        for idx, organization in enumerate(organizations):
            prefix = f"{idx + 1} of {organizations_count}"
            print(f"{prefix:<10} {organization.url}\n")

            if organization.related_projects.count() != 1:
                logger.error(
                    "Couldn't identify related project for external organization %s. "
                    "The related projects: %s.",
                    organization,
                    organization.related_projects,
                )
                continue

            gh_organization = gh.get_organization(organization.login)
            gh_repositories = gh_organization.get_repos(
                type="public",
                sort="created",
                direction="desc",
            )
            gh_repositories_count = gh_repositories.totalCount
            for idx_repository, gh_repository in enumerate(gh_repositories):
                prefix = f"{idx_repository + 1} of {gh_repositories_count}"
                repository_url = (
                    f"https://github.com/{organization.login}/{gh_repository.name.lower()}"
                )
                print(f"{prefix:<12} {repository_url}")

                try:
                    _, repository = sync_repository(gh_repository)
                    organization.related_projects.first().repositories.add(repository)
                except Exception:
                    logger.exception("Error syncing repository %s", repository_url)
                    continue
