"""A command to update OWASP entities related repositories data."""

import logging
import os

import github
from django.core.management.base import BaseCommand
from github.GithubException import UnknownObjectException

from apps.github.constants import GITHUB_ITEMS_PER_PAGE
from apps.github.models import Release, fetch_repository_data
from apps.github.utils import get_repository_path
from apps.owasp.models import Project

logger = logging.getLogger(__name__)

BATCH_SIZE = 10


class Command(BaseCommand):
    help = "Updates OWASP entities based on their owasp.org data."

    def handle(self, *args, **_options):
        def save_data():
            """Save data to DB."""
            # Releases.
            Release.objects.bulk_create(r for r in releases if not r.id)
            Release.objects.bulk_update(
                (r for r in releases if r.id),
                fields=[field.name for field in Release._meta.fields if not field.primary_key],  # noqa: SLF001
            )
            releases.clear()

            # Projects.
            Project.objects.bulk_update(
                (p for p in projects),
                fields=[field.name for field in Project._meta.fields if not field.primary_key],  # noqa: SLF001
            )
            projects.clear()

        active_projects = Project.objects.filter(is_active=True).order_by(
            "owasp_repository__created_at"
        )

        gh = github.Github(os.getenv("GITHUB_TOKEN"), per_page=GITHUB_ITEMS_PER_PAGE)

        projects = []
        releases = []
        for idx, project in enumerate(active_projects):
            print(f"{idx + 1:<3}", project.owasp_url)

            repository_urls = project.repositories_raw.copy()
            for repository_url in repository_urls:
                repository_path = get_repository_path(repository_url)
                if not repository_path:
                    logger.info("Couldn't get repository path for %s", repository_url)
                    continue

                try:
                    gh_repository = gh.get_repo(repository_path)
                except UnknownObjectException as e:
                    if e.data["status"] == "404" and "Not Found" in e.data["message"]:
                        project.repositories_raw.remove(repository_url)
                        project.save(update_fields=("repositories_raw",))
                        continue

                organization, repository, new_releases = fetch_repository_data(gh_repository)
                if organization is not None:
                    organization.save()
                repository.save()
                project.repositories.add(repository)
                releases.extend(new_releases)

            projects.append(project)

            if idx % BATCH_SIZE == 0:
                save_data()

        # Save remaining data.
        save_data()
