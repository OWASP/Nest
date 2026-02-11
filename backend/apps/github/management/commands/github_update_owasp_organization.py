"""A command to update OWASP entities from GitHub data."""

import logging

from django.core.management.base import BaseCommand

from apps.core.utils import index
from apps.github.auth import get_github_client
from apps.github.common import sync_repository
from apps.github.models.repository import Repository
from apps.owasp.constants import OWASP_ORGANIZATION_NAME
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.project import Project

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Fetch OWASP GitHub repository and update relevant entities."""

    help = "Fetch OWASP GitHub repository and update relevant entities."

    def add_arguments(self, parser) -> None:
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument("--offset", default=0, required=False, type=int)
        parser.add_argument(
            "--repository",
            required=False,
            type=str,
            help="The OWASP organization's repository name (e.g. Nest, www-project-nest')",
        )

    def handle(self, *_args, **options) -> None:
        """Handle the command execution.

        Args:
            *_args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        with index.disable_indexing():
            gh = get_github_client()
            gh_owasp_organization = gh.get_organization(OWASP_ORGANIZATION_NAME)

            owasp_organization = None
            owasp_user = None

            chapters = []
            committees = []
            projects = []

            offset = options["offset"]
            repository = options["repository"]

            if repository:
                gh_repositories = [gh_owasp_organization.get_repo(repository)]
                gh_repositories_count = 1
            else:
                gh_repositories = gh_owasp_organization.get_repos(
                    type="public",
                    sort="created",
                    direction="desc",
                )
                gh_repositories_count = gh_repositories.totalCount  # type: ignore[attr-defined]

            for idx, gh_repository in enumerate(gh_repositories[offset:]):
                prefix = f"{idx + offset + 1} of {gh_repositories_count}"
                entity_key = gh_repository.name.lower()
                repository_url = f"https://github.com/OWASP/{entity_key}"
                self.stdout.write(f"{prefix:<12} {repository_url}")

                try:
                    owasp_organization, owasp_repository = sync_repository(
                        gh_repository,
                        organization=owasp_organization,
                        user=owasp_user,
                    )

                    # OWASP chapters.
                    if entity_key.startswith("www-chapter-"):
                        chapters.append(
                            Chapter.update_data(gh_repository, owasp_repository, save=False)
                        )

                    # OWASP projects.
                    elif entity_key.startswith("www-project-"):
                        projects.append(
                            Project.update_data(gh_repository, owasp_repository, save=False)
                        )

                    # OWASP committees.
                    elif entity_key.startswith("www-committee-"):
                        committees.append(
                            Committee.update_data(gh_repository, owasp_repository, save=False)
                        )
                except Exception:
                    logger.exception("Error syncing repository %s", repository_url)
                    continue

            Chapter.bulk_save(chapters)
            Committee.bulk_save(committees)
            Project.bulk_save(projects)

            if not repository:  # The entire organization is being synced.
                # Check repository counts.
                local_owasp_repositories_count = Repository.objects.filter(
                    is_owasp_repository=True,
                ).count()
                remote_owasp_repositories_count = gh_owasp_organization.public_repos
                has_same_repositories_count = (
                    local_owasp_repositories_count == remote_owasp_repositories_count
                )
                result = "==" if has_same_repositories_count else "!="
                self.stdout.write(
                    "\n"
                    f"OWASP GitHub repositories count {result} synced repositories count: "
                    f"{remote_owasp_repositories_count} {result} {local_owasp_repositories_count}"
                )

            gh.close()

            # Add OWASP repository to repositories list.
            for project in Project.objects.all():
                if project.owasp_repository:
                    project.repositories.add(project.owasp_repository)
