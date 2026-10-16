"""A command to update OWASP projects from owasp.org data."""

import logging
from html import unescape
from typing import Any
from urllib.parse import urlparse

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.html import strip_tags

from apps.github.utils import normalize_url
from apps.owasp.api_client import OwaspApiClient
from apps.owasp.models.enums.project import ProjectLevel
from apps.owasp.models.project import LEVEL_MAPPING, Project, compact_key
from apps.owasp.sync import OwaspSync

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync OWASP projects from owasp.org."

    def add_arguments(self, parser) -> None:
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument("--offset", default=0, required=False, type=int)

    def handle(self, *args, **options) -> None:
        """Handle the command execution.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.
                offset (int): The starting index for processing.

        """
        offset = options["offset"]
        records = OwaspApiClient().list_projects()
        if records is None:
            return

        with transaction.atomic():
            self.sync_records(records, offset)

    def repository_name(self, url: str) -> str:
        """Return the repository name from an OWASP repository URL.

        Args:
            url (str): URL from the project catalog.

        Returns:
            str: Repository name, or an empty string when the URL is not a repository.

        """
        parsed = urlparse(url)
        if parsed.netloc.lower().removeprefix("www.") != "github.com":
            return ""

        parts = [part for part in parsed.path.split("/") if part]
        try:
            owner, repository = parts
        except ValueError:
            return ""

        return repository if owner.lower() == "owasp" else ""

    def legacy_project_key(self, url: str) -> str:
        """Return a www-project key stored in a legacy project URL.

        Args:
            url (str): Public or legacy project URL.

        Returns:
            str: The ``www-project-`` key, or an empty string.

        """
        path = urlparse(url).path.strip("/").lower()
        return path if path.startswith("www-project-") else ""

    def matched_project(
        self,
        record: dict,
        projects: dict[str, Project],
        repository_index: dict[str, list[Project]],
    ) -> Project | None:
        """Find the local project a catalog record should update.

        Args:
            record (dict): One project from the OWASP catalog.
            projects (dict[str, Project]): Local projects keyed by lowercase project key.
            repository_index (dict[str, list[Project]]): Projects indexed by repository name.

        Returns:
            Project | None: The existing project, or None when the catalog row is new.

        """
        repository_name = self.repository_name(str(record.get("github_url") or ""))
        if repository_name:
            matches = repository_index.get(compact_key(repository_name), [])
            if len(matches) == 1:
                return matches[0]

        legacy_key = self.legacy_project_key(str(record.get("project_url") or ""))
        if legacy_key and legacy_key in projects:
            return projects[legacy_key]

        slug = str(record.get("slug") or "").strip().lower()
        return projects.get(slug) or projects.get(f"www-project-{slug}")

    def adopt_slug(self, project: Project, slug: str, projects: dict[str, Project]) -> None:
        """Store the project under the website slug in the local index.

        Args:
            project (Project): Project that should keep this catalog row.
            slug (str): Website slug.
            projects (dict[str, Project]): Local projects keyed by lowercase project key.

        """
        previous_key = project.key.lower()
        if previous_key == slug.lower():
            return

        if not project.adopt_key(slug, projects.get(slug.lower())):
            logger.warning(
                "Left project %s unchanged because %s already has repositories",
                project.key,
                slug,
            )
            return

        projects.pop(previous_key, None)
        projects[slug.lower()] = project

    def sync_records(self, records: list[dict[str, Any]], offset: int) -> None:
        """Update local projects from a complete catalog read.

        Args:
            records (list[dict]): Project records from owasp.org.
            offset (int): Number of catalog records to skip.

        """
        if any(not str(record.get("slug") or "").strip() for record in records):
            logger.warning("OWASP projects catalog row has no slug")
            return

        local_projects = {
            project.key.lower(): project
            for project in Project.objects.prefetch_related("repositories")
        }
        repository_index = Project.index_by_repository(local_projects)
        catalog = records[offset:]
        retained_keys = set()
        for record in catalog:
            slug = str(record.get("slug") or "").strip()
            if not slug:
                continue
            retained_keys.add(slug)
            if project := self.matched_project(record, local_projects, repository_index):
                retained_keys.add(project.key)

        if not retained_keys:
            return

        raw_levels = {level: raw for raw, level in LEVEL_MAPPING.items()}
        claimed_ids: set[int] = set()
        projects = []
        for idx, record in enumerate(catalog):
            slug = str(record.get("slug") or "").strip()
            if not slug:
                continue

            self.stdout.write(f"{idx + offset + 1} of {len(records)} {slug}\n")
            project = self.matched_project(record, local_projects, repository_index)
            if project is not None and project.pk in claimed_ids:
                project = local_projects.get(slug.lower())
                if project is not None and project.pk in claimed_ids:
                    project = None
            if project is None:
                project = Project(key=slug)
                local_projects[slug.lower()] = project
            else:
                self.adopt_slug(project, slug, local_projects)
            if project.pk:
                claimed_ids.add(project.pk)

            title = str(record.get("title") or "").strip()
            if title:
                project.name = title[:100]
            elif not project.name:
                project.name = slug[:100]

            if record.get("description"):
                description = unescape(strip_tags(str(record["description"])))
                project.description = " ".join(description.split())[:500]

            level = str(record.get("project_type") or "").strip().lower()
            if level:
                project.level = level if level in ProjectLevel.values else ProjectLevel.OTHER
                project.level_raw = raw_levels.get(project.level, "")

            if isinstance(record.get("tags"), list):
                project.tags = record["tags"]

            project.is_active = record.get("status") == "active"

            related_urls = set()
            for link in record.get("project_links") or []:
                if isinstance(link, dict):
                    related_urls.add(link.get("url"))
            for field in ("documentation_url", "github_url", "project_url", "website_url"):
                related_urls.add(record.get(field))
            project.related_urls = sorted(
                {
                    related_url
                    for url in related_urls
                    if url
                    and (related_url := normalize_url(str(url)))
                    and (related_url := project.get_related_url(related_url))
                    and related_url not in {project.github_url, project.owasp_url}
                }
            )

            leaders = {
                name: (leader.get("contact") or None)
                for leader in record.get("project_leaders") or []
                if isinstance(leader, dict) and (name := str(leader.get("name") or "").strip())
            }
            projects.append((project, leaders))

        new_projects = [project for project, _leaders in projects if not project.id]
        if new_projects:
            Project.bulk_save(new_projects)

        for project, leaders in projects:
            OwaspSync.apply_leaders(project, leaders)

        Project.bulk_save([project for project, _leaders in projects])

        # A partial run resumes writes. Only a full catalog pass reconciles absences.
        if offset == 0:
            for project in local_projects.values():
                if project.is_active and project.key not in retained_keys:
                    project.deactivate()
