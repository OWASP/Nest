"""A command to create chunks of OWASP chapter data for RAG."""

import os

import openai
from django.core.management.base import BaseCommand

from apps.ai.common.constants import DELIMITER
from apps.ai.common.utils import create_chunks_and_embeddings
from apps.ai.models.chunk import Chunk
from apps.owasp.models.chapter import Chapter


class Command(BaseCommand):
    help = "Create chunks for OWASP chapter data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--chapter",
            type=str,
            help="Process only the chapter with this key",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Process all the chapters",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=50,
            help="Number of chapters to process in each batch",
        )

    def handle(self, *args, **options):
        if not (openai_api_key := os.getenv("DJANGO_OPEN_AI_SECRET_KEY")):
            self.stdout.write(
                self.style.ERROR("DJANGO_OPEN_AI_SECRET_KEY environment variable not set")
            )
            return

        self.openai_client = openai.OpenAI(api_key=openai_api_key)

        if chapter := options["chapter"]:
            queryset = Chapter.objects.filter(key=chapter)
        elif options["all"]:
            queryset = Chapter.objects.all()
        else:
            queryset = Chapter.objects.filter(is_active=True)

        if not (total_chapters := queryset.count()):
            self.stdout.write("No chapters found to process")
            return

        self.stdout.write(f"Found {total_chapters} chapters to process")

        batch_size = options["batch_size"]
        for offset in range(0, total_chapters, batch_size):
            batch_chapters = queryset[offset : offset + batch_size]

            batch_chunks = []
            for chapter in batch_chapters:
                batch_chunks.extend(self.handle_chunks(chapter))

            if batch_chunks:
                Chunk.bulk_save(batch_chunks)
                self.stdout.write(f"Saved {len(batch_chunks)} chunks")

        self.stdout.write(f"Completed processing all {total_chapters} chapters")

    def handle_chunks(self, chapter: Chapter) -> list[Chunk]:
        """Create chunks from a chapter's data."""
        prose_content, metadata_content = self.extract_chapter_content(chapter)

        all_chunk_texts = []

        if metadata_content.strip():
            all_chunk_texts.append(metadata_content)

        if prose_content.strip():
            all_chunk_texts.extend(Chunk.split_text(prose_content))

        if not all_chunk_texts:
            self.stdout.write(f"No content to chunk for chapter {chapter.key}")
            return []

        return create_chunks_and_embeddings(
            all_chunk_texts=all_chunk_texts,
            content_object=chapter,
            openai_client=self.openai_client,
        )

    def extract_chapter_content(self, chapter: Chapter) -> tuple[str, str]:
        """Extract and separate prose content from metadata for a chapter.

        Returns:
          tuple[str, str]: (prose_content, metadata_content)

        """
        prose_parts = []
        metadata_parts = []

        # Prose content
        for field, label in [("description", "Description"), ("summary", "Summary")]:
            value = getattr(chapter, field, None)
            if value:
                prose_parts.append(f"{label}: {value}")

        # Repository content
        repo = getattr(chapter, "owasp_repository", None)
        if repo:
            if repo.description:
                prose_parts.append(f"Repository Description: {repo.description}")
            if repo.topics:
                metadata_parts.append(f"Repository Topics: {', '.join(repo.topics)}")

        if chapter.name:
            metadata_parts.append(f"Chapter Name: {chapter.name}")

        # Location information - combine into single operation
        location_parts = [
            f"{label}: {value}"
            for value, label in [
                (chapter.country, "Country"),
                (chapter.region, "Region"),
                (chapter.postal_code, "Postal Code"),
                (chapter.suggested_location, "Location"),
            ]
            if value
        ]
        if location_parts:
            metadata_parts.append(f"Location Information: {', '.join(location_parts)}")

        # Simple and list-based metadata fields
        for field, label in [
            ("currency", "Currency"),
            ("meetup_group", "Meetup Group"),
            ("tags", "Tags"),
            ("topics", "Topics"),
            ("leaders_raw", "Chapter Leaders"),
        ]:
            value = getattr(chapter, field, None)
            if value:
                display_value = ", ".join(value) if isinstance(value, list) else value
                metadata_parts.append(f"{label}: {display_value}")

        # Related URLs with validation
        if chapter.related_urls:
            valid_urls = [
                url
                for url in chapter.related_urls
                if url and url not in (chapter.invalid_urls or [])
            ]
            if valid_urls:
                metadata_parts.append(f"Related URLs: {', '.join(valid_urls)}")

        metadata_parts.append(f"Active Chapter: {'Yes' if chapter.is_active else 'No'}")

        return (
            DELIMITER.join(filter(None, prose_parts)),
            DELIMITER.join(filter(None, metadata_parts)),
        )
