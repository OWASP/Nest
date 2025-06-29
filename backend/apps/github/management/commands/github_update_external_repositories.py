"""A command to update external OWASP repositories from GitHub data."""

import logging
import os

import github
from django.core.management.base import BaseCommand
from github.GithubException import BadCredentialsException

from apps.github.common import sync_repository
from apps.github.constants import GITHUB_ITEMS_PER_PAGE
from apps.github.models.organization import Organization
from apps.owasp.constants import OWASP_ORGANIZATION_NAME

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Fetch external OWASP GitHub repositories and update relevant entities."""

    help = "Fetch external OWASP GitHub repositories and update relevant entities."

    def add_arguments(self, parser) -> None:
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument(
            "--organization",
            required=False,
            type=str,
            help="The organization name (e.g. juice-shop)",
        )

    def handle(self, *_args, **options) -> None:
        """Handle the command execution.

        Args:
            *_args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            logger.warning(
                "Github token not found, please update .env file with a valid GITHUB_TOKEN"
            )
            return

        gh = github.Github(github_token, per_page=GITHUB_ITEMS_PER_PAGE)

        ext_orgs = []
        org_count = 0
        organization = options["organization"]
        if organization:
            ext_org = Organization.objects.filter(login=organization).first()
            if not ext_org:
                logger.error("Organization '%s' not found in the database", organization)
                return
            ext_orgs = [ext_org]
            org_count = 1
        else:
            ext_orgs = Organization.objects.filter(is_owasp_related_organization=True).exclude(
                login=OWASP_ORGANIZATION_NAME
            )
            org_count = ext_orgs.count()

        for org_idx, ext_org in enumerate(ext_orgs):
            print(f"Processing organization {org_idx + 1}/{org_count}: {ext_org.login}")
            try:
                gh_organization = gh.get_organization(ext_org.login)
                gh_repositories = gh_organization.get_repos(
                    type="public",
                    sort="created",
                    direction="desc",
                )
            except BadCredentialsException:
                logger.warning("Invalid GitHub token. Please update .env file with a valid token.")
                return
            except Exception:
                logger.exception("Failed fetching GitHub repository for org %s", ext_org.login)
                continue

            self.sync_organization_repositories(ext_org, gh_repositories)

    def sync_organization_repositories(self, external_org, gh_repositories) -> None:
        """Sync GitHub repositories for a given external organization."""
        gh_repositories_count = gh_repositories.totalCount
        for repo_idx, gh_repository in enumerate(gh_repositories):
            entity_key = gh_repository.name.lower()
            org_key = external_org.login.lower()
            repository_url = f"https://github.com/{org_key}/{entity_key}"
            print(f"{repo_idx + 1}/{gh_repositories_count}: {repository_url}")

            try:
                sync_repository(gh_repository)
            except BadCredentialsException:
                logger.warning("Invalid GitHub token. Please update .env file with a valid token.")
                return
            except Exception:
                logger.exception("Error syncing repository %s", repository_url)
                continue
