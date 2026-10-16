"""A command to update OWASP chapters from owasp.org data."""

from html import unescape
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.html import strip_tags

from apps.github.utils import normalize_url
from apps.owasp.api_client import OwaspApiClient
from apps.owasp.models.chapter import Chapter
from apps.owasp.sync import OwaspSync


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

        with transaction.atomic():
            self.sync_records(records, offset)

    def matched_chapter(self, record: dict, chapters: dict[str, Chapter]) -> Chapter | None:
        """Find the local chapter a catalog record should update.

        Args:
            record (dict): One chapter from the OWASP catalog.
            chapters (dict[str, Chapter]): Local chapters keyed by lowercase chapter key.

        Returns:
            Chapter | None: The existing chapter, or None when the catalog row is new.

        """
        slug = str(record.get("slug") or "").strip().lower()
        if not slug:
            return None

        return chapters.get(slug) or chapters.get(f"www-chapter-{slug}")

    def adopt_slug(self, chapter: Chapter, slug: str, chapters: dict[str, Chapter]) -> None:
        """Store the chapter under the website slug.

        An empty chapter already using that slug is removed so the populated chapter can take it.

        Args:
            chapter (Chapter): Chapter that should keep this catalog row.
            slug (str): Website slug.
            chapters (dict[str, Chapter]): Local chapters keyed by lowercase chapter key.

        """
        if chapter.key.lower() == slug.lower():
            return

        stub = chapters.get(slug.lower())
        if stub is not None and stub is not chapter:
            if stub.pk:
                stub.delete()
            chapters.pop(slug.lower(), None)

        chapters.pop(chapter.key.lower(), None)
        chapter.key = slug
        chapters[slug.lower()] = chapter

    def sync_records(self, records: list[dict[str, Any]], offset: int) -> None:
        """Update local chapters from a complete catalog read.

        Args:
            records (list[dict]): Chapter records from owasp.org.
            offset (int): Number of catalog records to skip.

        """
        local_chapters = {chapter.key.lower(): chapter for chapter in Chapter.objects.all()}
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
        for idx, record in enumerate(records[offset:]):
            slug = str(record.get("slug") or "").strip()
            if not slug:
                continue

            self.stdout.write(f"{idx + offset + 1} of {len(records)} {slug}\n")
            chapter = self.matched_chapter(record, local_chapters)
            if chapter is None:
                chapter = Chapter(key=slug)
                local_chapters[slug.lower()] = chapter
            else:
                self.adopt_slug(chapter, slug, local_chapters)

            name = str(record.get("name") or "").strip()
            if name:
                chapter.name = name[:100]
            elif not chapter.name:
                chapter.name = slug[:100]

            if record.get("description"):
                description = unescape(strip_tags(str(record["description"])))
                chapter.description = " ".join(description.split())[:500]

            for field in ("country", "region"):
                value = str(record.get(field) or "").strip()
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
            chapters.append((chapter, leaders))

        new_chapters = [chapter for chapter, _leaders in chapters if not chapter.id]
        if new_chapters:
            Chapter.bulk_save(new_chapters)

        for chapter, leaders in chapters:
            OwaspSync.apply_leaders(chapter, leaders)

        Chapter.bulk_save([chapter for chapter, _leaders in chapters])

        for chapter in local_chapters.values():
            if chapter.is_active and chapter.key not in retained_keys:
                chapter.deactivate()
