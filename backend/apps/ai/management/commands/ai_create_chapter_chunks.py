"""A command to create chunks of OWASP chapter data for RAG."""

import os

import openai
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.ai.common.constants import DELIMITER
from apps.ai.common.utils import create_chunks_and_embeddings, create_context
from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context
from apps.owasp.models.chapter import Chapter


class Command(BaseCommand):
    help = "Create chunks for OWASP chapter data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--chapter-key",
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
        parser.add_argument(
            "--context",
            action="store_true",
            help="Create only context (skip chunks and embeddings)",
        )
        parser.add_argument(
            "--chunks",
            action="store_true",
            help="Create only chunks+embeddings (requires existing context)",
        )

    def handle(self, *args, **options):
        if not options["context"] and not options["chunks"]:
            self.stdout.write(
                self.style.ERROR("Please specify either --context or --chunks (or both)")
            )
            return

        if options["chunks"] and not (openai_api_key := os.getenv("DJANGO_OPEN_AI_SECRET_KEY")):
            self.stdout.write(
                self.style.ERROR("DJANGO_OPEN_AI_SECRET_KEY environment variable not set")
            )
            return

        if options["chunks"]:
            self.openai_client = openai.OpenAI(api_key=openai_api_key)

        if options["chapter_key"]:
            queryset = Chapter.objects.filter(key=options["chapter_key"])
        elif options["all"]:
            queryset = Chapter.objects.all()
        else:
            queryset = Chapter.objects.filter(is_active=True)

        if not (total_chapters := queryset.count()):
            self.stdout.write("No chapters found to process")
            return

        self.stdout.write(f"Found {total_chapters} chapters to process")

        batch_size = options["batch_size"]
        processed_count = 0

        for offset in range(0, total_chapters, batch_size):
            batch_chapters = queryset[offset : offset + batch_size]

            if options["context"]:
                processed_count += self.process_context_batch(batch_chapters)
            elif options["chunks"]:
                processed_count += self.process_chunks_batch(batch_chapters)

        self.stdout.write(
            self.style.SUCCESS(f"Completed processing {processed_count}/{total_chapters} chapters")
        )

    def process_context_batch(self, chapters: list[Chapter]) -> int:
        """Process a batch of chapters to create contexts."""
        processed = 0

        for chapter in chapters:
            prose_content, metadata_content = self.extract_chapter_content(chapter)
            full_content = (
                f"{metadata_content}\n\n{prose_content}" if metadata_content else prose_content
            )

            if not full_content.strip():
                self.stdout.write(f"No content for chapter {chapter.key}")
                continue

            if create_context(
                content=full_content, content_object=chapter, source="owasp_chapter"
            ):
                processed += 1
                self.stdout.write(f"Created context for {chapter.key}")
            else:
                self.stdout.write(self.style.ERROR(f"Failed to create context for {chapter.key}"))
        return processed

    def process_chunks_batch(self, chapters: list[Chapter]) -> int:
        """Process a batch of chapters to create chunks."""
        processed = 0
        batch_chunks = []

        chapter_content_type = ContentType.objects.get_for_model(Chapter)

        for chapter in chapters:
            context = Context.objects.filter(
                content_type=chapter_content_type, object_id=chapter.id
            ).first()

            if not context:
                self.stdout.write(
                    self.style.WARNING(f"No context found for chapter {chapter.key}")
                )
                continue

            prose_content, metadata_content = self.extract_chapter_content(chapter)
            all_chunk_texts = []

            if metadata_content.strip():
                all_chunk_texts.append(metadata_content)

            if prose_content.strip():
                prose_chunks = Chunk.split_text(prose_content)
                all_chunk_texts.extend(prose_chunks)

            if not all_chunk_texts:
                self.stdout.write(f"No content to chunk for chapter {chapter.key}")
                continue

            if chunks := create_chunks_and_embeddings(
                chunk_texts=all_chunk_texts,
                context=context,
                openai_client=self.openai_client,
                save=False,
            ):
                batch_chunks.extend(chunks)
                processed += 1
                self.stdout.write(f"Created {len(chunks)} chunks for {chapter.key}")

        if batch_chunks:
            Chunk.bulk_save(batch_chunks)
        return processed

    def extract_chapter_content(self, chapter: Chapter) -> tuple[str, str]:
        """Extract and separate prose content from metadata for a chapter.

        Returns:
          tuple[str, str]: (prose_content, metadata_content)

        """
        prose_parts = []
        metadata_parts = []

        if chapter.description:
            prose_parts.append(f"Description: {chapter.description}")

        if chapter.summary:
            prose_parts.append(f"Summary: {chapter.summary}")

        if hasattr(chapter, "owasp_repository") and chapter.owasp_repository:
            repo = chapter.owasp_repository
            if repo.description:
                prose_parts.append(f"Repository Description: {repo.description}")
            if repo.topics:
                metadata_parts.append(f"Repository Topics: {', '.join(repo.topics)}")

        if chapter.name:
            metadata_parts.append(f"Chapter Name: {chapter.name}")

        location_parts = []
        if chapter.country:
            location_parts.append(f"Country: {chapter.country}")
        if chapter.region:
            location_parts.append(f"Region: {chapter.region}")
        if chapter.postal_code:
            location_parts.append(f"Postal Code: {chapter.postal_code}")
        if chapter.suggested_location:
            location_parts.append(f"Location: {chapter.suggested_location}")

        if location_parts:
            metadata_parts.append(f"Location Information: {', '.join(location_parts)}")

        if chapter.currency:
            metadata_parts.append(f"Currency: {chapter.currency}")

        if chapter.meetup_group:
            metadata_parts.append(f"Meetup Group: {chapter.meetup_group}")

        if chapter.tags:
            metadata_parts.append(f"Tags: {', '.join(chapter.tags)}")

        if chapter.topics:
            metadata_parts.append(f"Topics: {', '.join(chapter.topics)}")

        if chapter.leaders_raw:
            metadata_parts.append(f"Chapter Leaders: {', '.join(chapter.leaders_raw)}")

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
