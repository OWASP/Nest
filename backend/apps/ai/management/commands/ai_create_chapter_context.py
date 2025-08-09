"""A command to update context for OWASP chapter data."""

from django.core.management.base import BaseCommand

from apps.ai.common.extractors import extract_chapter_content
from apps.ai.common.utils import create_context
from apps.owasp.models.chapter import Chapter


class Command(BaseCommand):
    help = "Update context for OWASP chapter data"

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
            processed_count += self.process_context_batch(batch_chapters)

        self.stdout.write(
            self.style.SUCCESS(f"Completed processing {processed_count}/{total_chapters} chapters")
        )

    def process_context_batch(self, chapters: list[Chapter]) -> int:
        """Process a batch of chapters to create contexts."""
        processed = 0

        for chapter in chapters:
            prose_content, metadata_content = extract_chapter_content(chapter)
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
