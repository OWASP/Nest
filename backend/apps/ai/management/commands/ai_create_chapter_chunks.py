"""A command to create chunks of OWASP chapter data for RAG."""

import os

import openai
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.ai.common.extractors import extract_chapter_content
from apps.ai.common.utils import create_chunks_and_embeddings
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

    def handle(self, *args, **options):
        if not (openai_api_key := os.getenv("DJANGO_OPEN_AI_SECRET_KEY")):
            self.stdout.write(
                self.style.ERROR("DJANGO_OPEN_AI_SECRET_KEY environment variable not set")
            )
            return

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
            processed_count += self.process_chunks_batch(batch_chapters)

        self.stdout.write(
            self.style.SUCCESS(f"Completed processing {processed_count}/{total_chapters} chapters")
        )

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

            prose_content, metadata_content = extract_chapter_content(chapter)
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
