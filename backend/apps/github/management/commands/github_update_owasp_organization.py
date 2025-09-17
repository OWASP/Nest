"""A command to update OWASP entities from GitHub data."""

import logging
import time
from http import HTTPStatus
from urllib.parse import urlparse

import requests
from django.core.management.base import BaseCommand
from github.GithubException import GithubException, UnknownObjectException

from apps.core.utils import index
from apps.github.auth import get_github_client
from apps.github.common import sync_repository
from apps.github.constants import GITHUB_USER_RE
from apps.github.models.repository import Repository
from apps.github.utils import normalize_url
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
                print(f"{prefix:<12} {repository_url}")

                try:
                    owasp_organization, synced_repository = sync_repository(
                        gh_repository,
                        organization=owasp_organization,
                        user=owasp_user,
                    )

                    # OWASP chapters.
                    if entity_key.startswith("www-chapter-"):
                        chapters.append(
                            Chapter.update_data(gh_repository, synced_repository, save=False)
                        )

                    # OWASP projects.
                    elif entity_key.startswith("www-project-"):
                        projects.append(
                            Project.update_data(gh_repository, synced_repository, save=False)
                        )

                    # OWASP committees.
                    elif entity_key.startswith("www-committee-"):
                        committees.append(
                            Committee.update_data(gh_repository, synced_repository, save=False)
                        )
                except Exception:
                    logger.exception("Error syncing repository %s", repository_url)
                    continue

            Chapter.bulk_save(chapters)
            Committee.bulk_save(committees)
            Project.bulk_save(projects)

            if repository is None:  # The entire organization is being synced.
                # Sync markdown data
                self._sync_entity_markdown_data(Chapter, "active_chapters", gh)
                self._sync_entity_markdown_data(Committee, "active_committees", gh)
                self._sync_entity_markdown_data(Project, "active_projects", gh)

                # Check repository counts.
                local_owasp_repositories_count = Repository.objects.filter(
                    is_owasp_repository=True,
                ).count()
                remote_owasp_repositories_count = gh_owasp_organization.public_repos
                has_same_repositories_count = (
                    local_owasp_repositories_count == remote_owasp_repositories_count
                )
                result = "==" if has_same_repositories_count else "!="
                print(
                    "\n"
                    f"OWASP GitHub repositories count {result} synced repositories count: "
                    f"{remote_owasp_repositories_count} {result} {local_owasp_repositories_count}"
                )

            gh.close()

            # Add OWASP repository to repositories list.
            for project in Project.objects.all():
                if project.owasp_repository:
                    project.repositories.add(project.owasp_repository)

    def _sync_entity_markdown_data(self, model_class, manager_name, gh):
        """Sync additional data from markdown files for active OWASP entities."""
        model_manager = getattr(model_class, manager_name, model_class.objects)
        active_entities = model_manager.order_by("-created_at")
        active_entities_count = active_entities.count()

        entities = []
        for idx, entity in enumerate(active_entities):
            prefix = f"{idx + 1} of {active_entities_count}"
            print(f"{prefix:<10} {entity.owasp_url}")

            if not self._validate_github_repo(gh, entity):
                continue

            entity.leaders_raw = entity.get_leaders()
            if leaders_emails := entity.get_leaders_emails():
                entity.sync_leaders(leaders_emails)

            if isinstance(entity, Project):
                entity.audience = entity.get_audience()
                entity.invalid_urls, entity.related_urls = self._get_project_urls(entity, gh)
            else:
                entity.invalid_urls, entity.related_urls = self._get_generic_urls(entity)

            entities.append(entity)

            time.sleep(0.5)

        model_class.bulk_save(entities)

    def _get_project_urls(self, project, gh):
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
            verified_url = self._verify_url(scraped_url)
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

        return sorted(invalid_urls), sorted(related_urls)

    def _get_generic_urls(self, entity):
        scraped_urls = sorted(
            {
                repository_url
                for url in set(entity.get_urls())
                if (
                    repository_url := normalize_url(
                        entity.get_related_url(url, exclude_domains=("github.com", "owasp.org"))
                    )
                )
                and repository_url not in {entity.github_url, entity.owasp_url}
            }
        )

        invalid_urls = set()
        related_urls = set()
        for scraped_url in scraped_urls:
            verified_url = self._verify_url(scraped_url)
            if not verified_url:
                invalid_urls.add(scraped_url)
                continue

            if verified_url := entity.get_related_url(
                normalize_url(verified_url, check_path=True)
            ):
                related_urls.add(verified_url)
            else:
                logger.info("Skipped related URL %s", verified_url)

        return sorted(invalid_urls), sorted(related_urls)

    def _validate_github_repo(self, gh, entity) -> bool:
        """Validate if GitHub repository exists for an entity."""
        try:
            gh.get_repo(f"owasp/{entity.key}")
        except UnknownObjectException:
            entity.deactivate()
            return False
        except GithubException as e:
            logger.warning("GitHub API error for %s: %s", entity.key, e)
            time.sleep(1)
            return False
        else:
            return True

    def _verify_url(self, url):
        """Verify URL."""
        location = urlparse(url).netloc.lower()
        if not location:
            return None

        if location.endswith(("linkedin.com", "slack.com", "youtube.com")):
            return url

        try:
            # Check for redirects.
            response = requests.get(url, allow_redirects=False, timeout=(5, 10))
        except requests.exceptions.RequestException:
            logger.exception("Request failed", extra={"url": url})
            return None

        if response.status_code == HTTPStatus.OK:
            return url

        if response.status_code in {
            HTTPStatus.MOVED_PERMANENTLY,  # 301
            HTTPStatus.FOUND,  # 302
            HTTPStatus.SEE_OTHER,  # 303
            HTTPStatus.TEMPORARY_REDIRECT,  # 307
            HTTPStatus.PERMANENT_REDIRECT,  # 308
        }:
            return self._verify_url(response.headers["Location"])

        logger.warning("Couldn't verify URL %s", url)

        return None
