"""A command to update OWASP entities from GitHub data."""

import os

import github
from django.core.management.base import BaseCommand

from apps.github.constants import GITHUB_ITEMS_PER_PAGE
from apps.github.models import Issue, Organization, Release, Repository, sync_repository
from apps.owasp.constants import OWASP_ORGANIZATION_NAME
from apps.owasp.models import Chapter, Committee, Event, Project

BATCH_SIZE = 10


class Command(BaseCommand):
    help = "Updates OWASP entities based on their GitHub data."

    def handle(self, *_args, **_options):
        def save_data():
            """Save data to DB."""
            Organization.bulk_save(organizations)
            Issue.bulk_save(issues)
            Release.bulk_save(releases)

            Chapter.bulk_save(chapters)
            Committee.bulk_save(committees)
            Event.bulk_save(events)
            Project.bulk_save(projects)

        gh = github.Github(os.getenv("GITHUB_TOKEN"), per_page=GITHUB_ITEMS_PER_PAGE)
        gh_owasp_organization = gh.get_organization(OWASP_ORGANIZATION_NAME)
        remote_owasp_repositories_count = gh_owasp_organization.public_repos

        owasp_organization = None
        owasp_user = None

        chapters = []
        committees = []
        events = []
        issues = []
        organizations = []
        projects = []
        releases = []
        for idx, gh_repository in enumerate(
            gh_owasp_organization.get_repos(type="public", sort="created", direction="asc")
        ):
            print(f"{idx + 1:<3} {gh_repository.name}")

            owasp_organization, repository, new_releases = sync_repository(
                gh_repository, organization=owasp_organization, user=owasp_user
            )
            if not owasp_organization.id:
                owasp_organization.save()

            releases.extend(new_releases)

            entity_key = gh_repository.name.lower()
            # OWASP chapters.
            if entity_key.startswith("www-chapter-"):
                chapters.append(Chapter.update_data(gh_repository, repository, save=False))

            # OWASP projects.
            elif entity_key.startswith("www-project-"):
                projects.append(Project.update_data(gh_repository, repository, save=False))

            # OWASP events.
            elif entity_key.startswith("www-event-"):
                events.append(Event.update_data(gh_repository, repository, save=False))

            # OWASP committees.
            elif entity_key.startswith("www-committee-"):
                committees.append(Committee.update_data(gh_repository, repository, save=False))

            if idx % BATCH_SIZE == 0:
                save_data()

        # Save remaining data.
        save_data()

        # Check repository counts.
        local_owasp_repositories_count = Repository.objects.filter(
            is_owasp_repository=True
        ).count()
        result = (
            "==" if remote_owasp_repositories_count == local_owasp_repositories_count else "!="
        )
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
