"""A command to update OWASP entities data."""

import os

from django.core.management.base import BaseCommand
from github import Github

from apps.github.models import Organization, Repository, User
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

        updated_organizations = set()
        updated_users = set()
        for gh_repository in owasp_org.get_repos(
            type="public",
            sort="created",
            direction="asc",
        )[:5]:
            # GitHub repository organization.
            gh_organization = gh_repository.organization
            if gh_organization is not None:
                try:
                    organization = Organization.objects.get(login=gh_organization.login)
                except Organization.DoesNotExist:
                    organization = Organization(login=gh_organization.login)

                if organization.login not in updated_organizations:
                    updated_organizations.add(organization.login)
                    organization.from_github(gh_organization)
                    organization.save()

            # GitHub repository owner.
            gh_user = gh_repository.owner
            if gh_user is not None:
                try:
                    user = User.objects.get(login=gh_user.login)
                except User.DoesNotExist:
                    user = User(login=gh_organization.login)

                if user.login not in updated_users:
                    updated_users.add(user.login)
                    user.from_github(gh_user)
                    user.save()

            key = gh_repository.name.lower()
            languages = gh_repository.get_languages()
            # GitHub repository.
            try:
                repository = Repository.objects.get(key=key)
                repository.from_github(
                    gh_repository,
                    languages=languages,
                    organization=organization,
                    user=user,
                )
                update_repositories.append(repository)
            except Repository.DoesNotExist:
                repository = Repository(key=key)
                repository.from_github(
                    gh_repository,
                    languages=languages,
                    organization=organization,
                    user=user,
                )
                create_repositories.append(repository)

            # OWASP project.
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
