"""A command to update OWASP entities data."""

import os

from django.core.management.base import BaseCommand
from github import Github

from apps.repository.models import Repository

BATCH_SIZE = 1000
ITEMS_PER_PAGE = 100
OWASP = "OWASP"


class Command(BaseCommand):
    help = "Updates OWASP entities based on their GitHub data."

    def handle(self, *_args, **_options):
        gh = Github(os.getenv("GITHUB_TOKEN"), per_page=ITEMS_PER_PAGE)
        owasp_org = gh.get_organization(OWASP)

        create_repositories = []
        update_repositories = []
        for gh_repository in owasp_org.get_repos(type="public", sort="created", direction="desc")[
            :10
        ]:
            repository_name = gh_repository.name.lower()
            if repository_name.startswith("www-project-"):
                try:
                    repository = Repository.objects.get(
                        name=repository_name,
                        platform=Repository.Platforms.GITHUB,
                    )
                    repository.from_github_response(gh_repository)
                    update_repositories.append(repository)
                except Repository.DoesNotExist:
                    print(repository_name, "Does not exist")
                    repository = Repository(
                        name=repository_name,
                        platform=Repository.Platforms.GITHUB,
                    )
                    repository.from_github_response(gh_repository)
                    create_repositories.append(repository)

        Repository.objects.bulk_create(create_repositories)
        Repository.objects.bulk_update(
            update_repositories,
            batch_size=BATCH_SIZE,
            fields=[field.name for field in Repository._meta.fields if not field.primary_key],  # noqa: SLF001
        )
