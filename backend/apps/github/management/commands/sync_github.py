"""A command to update OWASP entities data."""

import os

from django.core.management.base import BaseCommand
from github import Github

from apps.github.models import Repository
from apps.owasp.models import Project

BATCH_SIZE = 1000
ITEMS_PER_PAGE = 100
OWASP = "OWASP"


class Command(BaseCommand):
    help = "Updates OWASP entities based on their GitHub data."

    def handle(self, *_args, **_options):
        gh = Github(os.getenv("GITHUB_TOKEN"), per_page=ITEMS_PER_PAGE)
        owasp_org = gh.get_organization(OWASP)

        create_projects = []
        create_repositories = []
        update_projects = []
        update_repositories = []
        for gh_repository in owasp_org.get_repos(
            type="public",
            sort="created",
            direction="desc",
        )[:5]:
            key = gh_repository.name.lower()
            try:
                repository = Repository.objects.get(key=key, platform=Repository.Platforms.GITHUB)
                repository.from_github(gh_repository)
                update_repositories.append(repository)
            except Repository.DoesNotExist:
                repository = Repository(key=key, platform=Repository.Platforms.GITHUB)
                repository.from_github(gh_repository)
                create_repositories.append(repository)

            # Update projects.
            if key.startswith("www-project-"):
                try:
                    project = Project.objects.get(key=key)
                    project.from_github(gh_repository, repository)
                    update_projects.append(project)
                except Project.DoesNotExist:
                    project = Project(key=key)
                    project.from_github(gh_repository, repository)
                    create_projects.append(project)

        # Repositories.
        Repository.objects.bulk_create(create_repositories)
        Repository.objects.bulk_update(
            update_repositories,
            batch_size=BATCH_SIZE,
            fields=[field.name for field in Repository._meta.fields if not field.primary_key],  # noqa: SLF001
        )

        # Projects.
        Project.objects.bulk_create(create_projects)
        Project.objects.bulk_update(
            update_projects,
            batch_size=BATCH_SIZE,
            fields=[field.name for field in Project._meta.fields if not field.primary_key],  # noqa: SLF001
        )
