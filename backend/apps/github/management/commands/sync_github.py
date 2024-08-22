"""A command to update OWASP entities data."""

import os

from django.core.management.base import BaseCommand
from github import Github

from apps.github.models import Organization, Release, Repository, User
from apps.github.utils import get_node_id
from apps.owasp.models import Project

BATCH_SIZE = 10
ITEMS_PER_PAGE = 100
OWASP = "OWASP"


class Command(BaseCommand):
    help = "Updates OWASP entities based on their GitHub data."

    def save_data(self, *args, **kwargs):
        """Save data to DB."""
        # Repositories.
        create_repositories = kwargs["create_repositories"]
        update_repositories = kwargs["update_repositories"]
        Repository.objects.bulk_create(create_repositories)
        Repository.objects.bulk_update(
            update_repositories,
            fields=[field.name for field in Repository._meta.fields if not field.primary_key],  # noqa: SLF001
        )

        # Releases.
        create_releases = kwargs["create_releases"]
        update_releases = kwargs["update_releases"]
        Release.objects.bulk_create(create_releases)
        Release.objects.bulk_update(
            update_releases,
            fields=[field.name for field in Release._meta.fields if not field.primary_key],  # noqa: SLF001
        )

        # Projects.
        create_projects = kwargs["create_projects"]
        update_projects = kwargs["update_projects"]
        Project.objects.bulk_create(create_projects)
        Project.objects.bulk_update(
            update_projects,
            fields=[field.name for field in Project._meta.fields if not field.primary_key],  # noqa: SLF001
        )

        for collection in (
            create_projects,
            create_releases,
            create_repositories,
            update_projects,
            update_releases,
            update_repositories,
        ):
            collection.clear()

    def handle(self, *_args, **_options):
        gh = Github(os.getenv("GITHUB_TOKEN"), per_page=ITEMS_PER_PAGE)
        owasp_org = gh.get_organization(OWASP)

        create_projects = []
        create_releases = []
        create_repositories = []
        update_projects = []
        update_releases = []
        update_repositories = []

        updated_organizations = set()
        updated_users = set()
        for idx, gh_repository in enumerate(
            owasp_org.get_repos(
                type="public",
                sort="created",
                direction="desc",
            )[200:500]
        ):
            print(gh_repository.name)

            # GitHub repository organization.
            gh_organization = gh_repository.organization
            if gh_organization is not None:
                organization_node_id = get_node_id(gh_organization)
                try:
                    organization = Organization.objects.get(node_id=organization_node_id)
                except Organization.DoesNotExist:
                    organization = Organization(node_id=organization_node_id)

                if organization_node_id not in updated_organizations:
                    updated_organizations.add(organization_node_id)
                    organization.from_github(gh_organization)
                    organization.save()

            # GitHub repository owner.
            gh_user = gh_repository.owner
            if gh_user is not None:
                user_node_id = get_node_id(gh_user)
                try:
                    user = User.objects.get(node_id=user_node_id)
                except User.DoesNotExist:
                    user = User(node_id=user_node_id)

                if user_node_id not in updated_users:
                    updated_users.add(user_node_id)
                    user.from_github(gh_user)
                    user.save()

            # GitHub repository.
            languages = gh_repository.get_languages()
            repository_node_id = get_node_id(gh_repository)
            try:
                repository = Repository.objects.get(node_id=repository_node_id)
                repository.from_github(
                    gh_repository,
                    languages=languages,
                    organization=organization,
                    user=user,
                )
                update_repositories.append(repository)
            except Repository.DoesNotExist:
                repository = Repository(node_id=repository_node_id)
                repository.from_github(
                    gh_repository,
                    languages=languages,
                    organization=organization,
                    user=user,
                )
                create_repositories.append(repository)

            # GitHub repository releases.
            existing_release_node_ids = set(
                Release.objects.filter(repository=repository).values_list("node_id", flat=True)
                if repository.id
                else ()
            )
            for gh_release in gh_repository.get_releases():
                release_node_id = get_node_id(gh_release)
                if release_node_id in existing_release_node_ids:
                    break

                # GitHub release author.
                gh_user = gh_release.author
                if gh_user is not None:
                    author_node_id = get_node_id(gh_user)
                    try:
                        author = User.objects.get(node_id=author_node_id)
                    except User.DoesNotExist:
                        author = User(node_id=author_node_id)

                    if author_node_id not in updated_users:
                        updated_users.add(author_node_id)
                        author.from_github(gh_user)
                        author.save()

                # GitHub release.
                try:
                    release = Release.objects.get(node_id=release_node_id)
                    release.from_github(gh_release, author=author, repository=repository)
                    update_releases.append(release)
                except Release.DoesNotExist:
                    release = Release(node_id=release_node_id)
                    release.from_github(gh_release, author=author, repository=repository)
                    create_releases.append(release)

            # OWASP project.
            project_key = gh_repository.name.lower()
            if project_key.startswith("www-project-"):
                try:
                    project = Project.objects.get(key=project_key)
                    project.from_github(gh_repository, repository)
                    update_projects.append(project)
                except Project.DoesNotExist:
                    project = Project(key=project_key)
                    project.from_github(gh_repository, repository)
                    create_projects.append(project)

            if idx % BATCH_SIZE == 0:
                self.save_data(
                    create_projects=create_projects,
                    create_releases=create_releases,
                    create_repositories=create_repositories,
                    update_projects=update_projects,
                    update_releases=update_releases,
                    update_repositories=update_repositories,
                )

        # Save remaining data.
        self.save_data(
            create_projects=create_projects,
            create_releases=create_releases,
            create_repositories=create_repositories,
            update_projects=update_projects,
            update_releases=update_releases,
            update_repositories=update_repositories,
        )
