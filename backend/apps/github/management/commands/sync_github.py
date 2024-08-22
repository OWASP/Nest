"""A command to update OWASP entities data."""

import os

import github
from django.core.management.base import BaseCommand

from apps.github.models import Organization, Release, Repository, User
from apps.github.utils import get_is_owasp_site_repository, get_node_id
from apps.owasp.models import Chapter, Committee, Event, Project

BATCH_SIZE = 10
ITEMS_PER_PAGE = 100
OWASP = "OWASP"


class Command(BaseCommand):
    help = "Updates OWASP entities based on their GitHub data."

    def handle(self, *_args, **_options):
        def save_data():
            """Save data to DB."""
            # Repositories.
            Repository.objects.bulk_create(create_repositories)
            Repository.objects.bulk_update(
                update_repositories,
                fields=[field.name for field in Repository._meta.fields if not field.primary_key],  # noqa: SLF001
            )

            # Releases.
            Release.objects.bulk_create(create_releases)
            Release.objects.bulk_update(
                update_releases,
                fields=[field.name for field in Release._meta.fields if not field.primary_key],  # noqa: SLF001
            )

            # Chapters.
            Chapter.objects.bulk_create(create_chapters)
            Chapter.objects.bulk_update(
                update_chapters,
                fields=[field.name for field in Chapter._meta.fields if not field.primary_key],  # noqa: SLF001
            )

            # Committees.
            Committee.objects.bulk_create(create_committees)
            Committee.objects.bulk_update(
                update_committees,
                fields=[field.name for field in Committee._meta.fields if not field.primary_key],  # noqa: SLF001
            )

            # Projects.
            Event.objects.bulk_create(create_events)
            Event.objects.bulk_update(
                update_events,
                fields=[field.name for field in Event._meta.fields if not field.primary_key],  # noqa: SLF001
            )

            # Projects.
            Project.objects.bulk_create(create_projects)
            Project.objects.bulk_update(
                update_projects,
                fields=[field.name for field in Project._meta.fields if not field.primary_key],  # noqa: SLF001
            )

            for collection in (
                create_chapters,
                create_committees,
                create_events,
                create_projects,
                create_releases,
                create_repositories,
                update_chapters,
                update_committees,
                update_events,
                update_projects,
                update_releases,
                update_repositories,
            ):
                collection.clear()

        gh = github.Github(os.getenv("GITHUB_TOKEN"), per_page=ITEMS_PER_PAGE)
        owasp_org = gh.get_organization(OWASP)
        remote_repositories_count = owasp_org.public_repos
        owasp_user = None

        create_chapters = []
        create_committees = []
        create_events = []
        create_projects = []
        create_releases = []
        create_repositories = []
        update_chapters = []
        update_committees = []
        update_events = []
        update_projects = []
        update_releases = []
        update_repositories = []

        updated_organizations = set()
        updated_users = set()
        for idx, gh_repository in enumerate(
            owasp_org.get_repos(type="public", sort="created", direction="desc")[1195:]
        ):
            # The full sync takes 5 API calls per repository:
            #  - get repository
            #  - get repository languages
            #  - get repository releases
            #  - fetch repository index.md file
            #  - fetch repository FUNDING.yml file
            # TODO(arkid15r): consider using git checkout instead of API calls to fetch files.
            pre_api_call_count, _ = gh.rate_limiting

            # Update OWASP entities.
            entity_key = gh_repository.name.lower()
            is_owasp_site_repository = get_is_owasp_site_repository(entity_key)

            # GitHub repository organization.
            gh_organization = gh_repository.organization
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
            if owasp_user is None:
                gh_user = gh_repository.owner
                if gh_user is not None:
                    user_node_id = get_node_id(gh_user)
                    try:
                        owasp_user = User.objects.get(node_id=user_node_id)
                    except User.DoesNotExist:
                        owasp_user = User(node_id=user_node_id)
                    owasp_user.from_github(gh_user)
                    owasp_user.save()

            # GitHub repository.
            languages = None if is_owasp_site_repository else gh_repository.get_languages()
            repository_node_id = get_node_id(gh_repository)
            try:
                repository = Repository.objects.get(node_id=repository_node_id)
                repository.from_github(
                    gh_repository,
                    languages=languages,
                    organization=organization,
                    user=owasp_user,
                )
                update_repositories.append(repository)
            except Repository.DoesNotExist:
                repository = Repository(node_id=repository_node_id)
                repository.from_github(
                    gh_repository,
                    languages=languages,
                    organization=organization,
                    user=owasp_user,
                )
                create_repositories.append(repository)

            # GitHub repository releases.
            if not is_owasp_site_repository:
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

            # OWASP chapters.
            if entity_key.startswith("www-chapter-"):
                try:
                    chapter = Chapter.objects.get(key=entity_key)
                    chapter.from_github(gh_repository, repository)
                    update_chapters.append(chapter)
                except Chapter.DoesNotExist:
                    chapter = Chapter(key=entity_key)
                    chapter.from_github(gh_repository, repository)
                    create_chapters.append(chapter)

            # OWASP projects.
            elif entity_key.startswith("www-project-"):
                try:
                    project = Project.objects.get(key=entity_key)
                    project.from_github(gh_repository, repository)
                    update_projects.append(project)
                except Project.DoesNotExist:
                    project = Project(key=entity_key)
                    project.from_github(gh_repository, repository)
                    create_projects.append(project)

            # OWASP events.
            elif entity_key.startswith("www-event-"):
                try:
                    event = Event.objects.get(key=entity_key)
                    event.from_github(gh_repository, repository)
                    update_events.append(event)
                except Event.DoesNotExist:
                    event = Event(key=entity_key)
                    event.from_github(gh_repository, repository)
                    create_events.append(event)

            # OWASP committees.
            elif entity_key.startswith("www-committee-"):
                try:
                    committee = Committee.objects.get(key=entity_key)
                    committee.from_github(gh_repository, repository)
                    update_committees.append(committee)
                except Committee.DoesNotExist:
                    committee = Committee(key=entity_key)
                    committee.from_github(gh_repository, repository)
                    create_committees.append(committee)

            if idx % BATCH_SIZE == 0:
                save_data()
            post_api_call_count, api_call_limit = gh.rate_limiting
            print(
                f"{idx + 1}. {gh_repository.name}",
                f"{pre_api_call_count - post_api_call_count} calls used, "
                f"{post_api_call_count} of {api_call_limit} calls left",
            )

        # Save remaining data.
        save_data()

        # Check repo counts.
        local_repositories_count = Repository.objects.count()
        result = "==" if remote_repositories_count == local_repositories_count else "!="
        print(
            "\n"
            f"OWASP GitHub repositories count {result} synced repositories count: "
            f"{remote_repositories_count} {result} {local_repositories_count}"
        )

        gh.close()
