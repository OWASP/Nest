"""A command to update OWASP chapters from owasp.org data."""

import logging
from html import unescape
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.html import strip_tags

from apps.github.utils import normalize_url
from apps.owasp.api_client import OwaspApiClient
from apps.owasp.models.chapter import Chapter
from apps.owasp.sync import OwaspSync

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync OWASP chapters from owasp.org."

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
        records = OwaspApiClient().list_chapters()
        if records is None:
            return

        self.sync_records(records, offset)

    def matched_chapter(self, record: dict, chapters: dict[str, Chapter]) -> Chapter | None:
        """Find the local chapter a catalog record should update.

        When the slug row has no repository and the ``www-chapter-`` row does, the row with the
        repository is the one to keep.

        Args:
            record (dict): One chapter from the OWASP catalog.
            chapters (dict[str, Chapter]): Local chapters keyed by lowercase chapter key.

        Returns:
            Chapter | None: The existing chapter, or None when the catalog row is new.

        """
        slug = str(record.get("slug") or "").strip().lower()
        if not slug:
            return None

        current = chapters.get(slug)
        legacy = chapters.get(f"www-chapter-{slug}")
        if (
            current is not None
            and legacy is not None
            and current is not legacy
            and not current.owasp_repository_id
            and legacy.owasp_repository_id
        ):
            return legacy

        return current or legacy

    def adopt_slug(
        self,
        chapter: Chapter,
        slug: str,
        chapters: dict[str, Chapter],
    ) -> Chapter | None:
        """Store the chapter under the website slug.

        A saved chapter with no linked repository is returned so the caller can remove that stub.
        A chapter that already has a repository keeps the slug.

        Args:
            chapter (Chapter): Chapter that should keep this catalog row.
            slug (str): Website slug.
            chapters (dict[str, Chapter]): Local chapters keyed by lowercase chapter key.

        Returns:
            Chapter | None: The stub that occupied the slug, when one must be removed.

        """
        previous_key = chapter.key.lower()
        if previous_key == slug.lower():
            return None

        occupant = chapters.get(slug.lower())
        if not chapter.adopt_key(slug, occupant):
            logger.warning(
                "Left chapter %s unchanged because %s already has a repository",
                chapter.key,
                slug,
            )
            return None

        removed = None
        if occupant is not None and occupant is not chapter and occupant.pk:
            removed = occupant
            chapters.pop(slug.lower(), None)

        chapters.pop(previous_key, None)
        chapters[slug.lower()] = chapter
        return removed

    def sync_records(self, records: list[dict[str, Any]], offset: int) -> None:
        """Update local chapters from a complete catalog read.

        Args:
            records (list[dict]): Chapter records from owasp.org.
            offset (int): Number of catalog records to skip.

        """
        if any(not str(record.get("slug") or "").strip() for record in records):
            logger.warning("OWASP chapters catalog row has no slug")
            return

        local_chapters = {
            chapter.key.lower(): chapter
            for chapter in Chapter.objects.select_related("owasp_repository")
        }
        retained_keys = set()
        for record in records:
            slug = str(record.get("slug") or "").strip()
            if not slug:
                continue
            retained_keys.add(slug)
            if chapter := self.matched_chapter(record, local_chapters):
                retained_keys.add(chapter.key)

        if not retained_keys:
            return

        chapters = []
        removed_chapters = []
        for idx, record in enumerate(records[offset:]):
            slug = str(record.get("slug") or "").strip()
            if not slug:
                continue

            self.stdout.write(f"{idx + offset + 1} of {len(records)} {slug}\n")
            chapter = self.matched_chapter(record, local_chapters)
            if chapter is None:
                chapter = Chapter(key=slug)
                local_chapters[slug.lower()] = chapter
            elif removed := self.adopt_slug(chapter, slug, local_chapters):
                removed_chapters.append(removed)

            name = str(record.get("name") or "").strip()
            if name:
                chapter.name = name[:100]
            elif not chapter.name:
                chapter.name = slug[:100]

            if record.get("description"):
                description = unescape(strip_tags(str(record["description"])))
                chapter.description = " ".join(description.split())[:500]

            location_changed = False
            for field in ("country", "region"):
                value = str(record.get(field) or "").strip()
                if value and getattr(chapter, field) != value:
                    location_changed = True
                    chapter.suggested_location = ""
                if value:
                    setattr(chapter, field, value[:50])

            chapter.is_active = bool(record.get("is_active"))

            related_urls = set()
            for link in record.get("social_links") or []:
                if isinstance(link, dict):
                    related_urls.add(link.get("url"))
            for field in ("meetup_url", "website_url"):
                related_urls.add(record.get(field))
            chapter.related_urls = sorted(
                {
                    related_url
                    for url in related_urls
                    if url
                    and (related_url := normalize_url(str(url)))
                    and (related_url := chapter.get_related_url(related_url))
                    and related_url not in {chapter.github_url, chapter.owasp_url}
                }
            )

            leaders = {
                leader_name: (leader.get("contact") or None)
                for leader in record.get("leadership_team") or []
                if isinstance(leader, dict)
                and (leader_name := str(leader.get("name") or "").strip())
            }
            chapters.append((chapter, leaders, location_changed))

        for chapter, _leaders, location_changed in chapters:
            if (
                chapter.latitude is not None
                and chapter.longitude is not None
                and not location_changed
            ):
                continue
            try:
                chapter.generate_geo_location()
            except Exception:
                logger.exception(
                    "Could not get geo data for chapter",
                    extra={"key": chapter.key},
                )

        with transaction.atomic():
            for chapter in removed_chapters:
                chapter.delete()

            new_chapters = [chapter for chapter, _leaders, _changed in chapters if not chapter.id]
            if new_chapters:
                Chapter.bulk_save(new_chapters)

            for chapter, leaders, _changed in chapters:
                OwaspSync.apply_leaders(chapter, leaders)

            Chapter.bulk_save([chapter for chapter, _leaders, _changed in chapters])

            for chapter in local_chapters.values():
                if chapter.is_active and chapter.key not in retained_keys:
                    chapter.deactivate()
