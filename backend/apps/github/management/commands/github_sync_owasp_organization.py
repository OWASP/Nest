"""A command to update OWASP entities from GitHub data."""

import os

import github
from django.core.management.base import BaseCommand

from apps.github.constants import GITHUB_ITEMS_PER_PAGE
from apps.github.models import Organization, Release, Repository, fetch_repository_data
from apps.owasp.constants import OWASP_ORGANIZATION_NAME
from apps.owasp.models import Chapter, Committee, Event, Project

BATCH_SIZE = 100


class Command(BaseCommand):
    help = "Updates OWASP entities based on their GitHub data."

    def handle(self, *_args, **_options):
        def save_data():
            """Save data to DB."""
            # Organizations.
            Organization.objects.bulk_create(o for o in organizations if not o.id)
            Organization.objects.bulk_update(
                (o for o in organizations if o.id),
                fields=[
                    field.name
                    for field in Organization._meta.fields  # noqa: SLF001
                    if not field.primary_key
                ],
            )
            organizations.clear()

            # Repositories.
            Repository.objects.bulk_create(r for r in repositories if not r.id)
            Repository.objects.bulk_update(
                [r for r in repositories if r.id],
                fields=[field.name for field in Repository._meta.fields if not field.primary_key],  # noqa: SLF001
            )
            repositories.clear()

            # Releases.
            Release.objects.bulk_create(r for r in releases if not r.id)
            Release.objects.bulk_update(
                (r for r in releases if r.id),
                fields=[field.name for field in Release._meta.fields if not field.primary_key],  # noqa: SLF001
            )
            releases.clear()

            # Chapters.
            Chapter.objects.bulk_create(c for c in chapters if not c.id)
            Chapter.objects.bulk_update(
                (c for c in chapters if c.id),
                fields=[field.name for field in Chapter._meta.fields if not field.primary_key],  # noqa: SLF001
            )
            chapters.clear()

            # Committees.
            Committee.objects.bulk_create(c for c in committees if not c.id)
            Committee.objects.bulk_update(
                (c for c in committees if c.id),
                fields=[field.name for field in Committee._meta.fields if not field.primary_key],  # noqa: SLF001
            )

            # Events.
            Event.objects.bulk_create(e for e in events if not e.id)
            Event.objects.bulk_update(
                [e for e in events if not e.id],
                fields=[field.name for field in Event._meta.fields if not field.primary_key],  # noqa: SLF001
            )

            # Projects.
            Project.objects.bulk_create(p for p in projects if not p.id)
            Project.objects.bulk_update(
                (p for p in projects if p.id),
                fields=[field.name for field in Project._meta.fields if not field.primary_key],  # noqa: SLF001
            )

        gh = github.Github(os.getenv("GITHUB_TOKEN"), per_page=GITHUB_ITEMS_PER_PAGE)
        gh_owasp_organization = gh.get_organization(OWASP_ORGANIZATION_NAME)
        remote_owasp_repositories_count = gh_owasp_organization.public_repos

        owasp_organization = None
        owasp_user = None

        chapters = []
        committees = []
        events = []
        organizations = []
        projects = []
        releases = []
        repositories = []
        for idx, gh_repository in enumerate(
            gh_owasp_organization.get_repos(type="public", sort="created", direction="desc")[0:]
        ):
            print(f"{idx + 1:<3} {gh_repository.name}")

            owasp_organization, new_repository, new_releases = fetch_repository_data(
                gh_repository, organization=owasp_organization, user=owasp_user
            )
            if not owasp_organization.id:
                owasp_organization.save()
            repositories.append(new_repository)
            releases.extend(new_releases)

            entity_key = gh_repository.name.lower()
            # OWASP chapters.
            if entity_key.startswith("www-chapter-"):
                try:
                    chapter = Chapter.objects.get(key=entity_key)
                except Chapter.DoesNotExist:
                    chapter = Chapter(key=entity_key)
                chapter.from_github(gh_repository, new_repository)
                chapters.append(chapter)

            # OWASP projects.
            elif entity_key.startswith("www-project-"):
                try:
                    project = Project.objects.get(key=entity_key)
                except Project.DoesNotExist:
                    project = Project(key=entity_key)
                project.from_github(gh_repository, new_repository)
                projects.append(project)

            # OWASP events.
            elif entity_key.startswith("www-event-"):
                try:
                    event = Event.objects.get(key=entity_key)
                except Event.DoesNotExist:
                    event = Event(key=entity_key)
                event.from_github(gh_repository, new_repository)
                events.append(event)

            # OWASP committees.
            elif entity_key.startswith("www-committee-"):
                try:
                    committee = Committee.objects.get(key=entity_key)
                except Committee.DoesNotExist:
                    committee = Committee(key=entity_key)
                committee.from_github(gh_repository, new_repository)
                committees.append(committee)

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
