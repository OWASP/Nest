"""A command to create chunks of OWASP committee data for RAG."""

import os

import openai
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.ai.common.extractors import extract_committee_content
from apps.ai.common.utils import create_chunks_and_embeddings
from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context
from apps.owasp.models.committee import Committee


class Command(BaseCommand):
    help = "Create chunks for OWASP committee data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--committee-key",
            type=str,
            help="Process only the committee with this key",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Process all the committees",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=50,
            help="Number of committees to process in each batch",
        )

    def handle(self, *args, **options):
        if not (openai_api_key := os.getenv("DJANGO_OPEN_AI_SECRET_KEY")):
            self.stdout.write(
                self.style.ERROR("DJANGO_OPEN_AI_SECRET_KEY environment variable not set")
            )
            return

        self.openai_client = openai.OpenAI(api_key=openai_api_key)

        if options["committee_key"]:
            queryset = Committee.objects.filter(key=options["committee_key"])
        elif options["all"]:
            queryset = Committee.objects.all()
        else:
            queryset = Committee.objects.filter(is_active=True)

        if not (total_committees := queryset.count()):
            self.stdout.write("No committees found to process")
            return

        self.stdout.write(f"Found {total_committees} committees to process")

        batch_size = options["batch_size"]
        processed_count = 0

        for offset in range(0, total_committees, batch_size):
            batch_committees = queryset[offset : offset + batch_size]
            processed_count += self.process_chunks_batch(batch_committees)

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed processing {processed_count}/{total_committees} committees"
            )
        )

    def process_chunks_batch(self, committees: list[Committee]) -> int:
        """Process a batch of committees to create chunks."""
        processed = 0
        batch_chunks = []

        committee_content_type = ContentType.objects.get_for_model(Committee)

        for committee in committees:
            context = Context.objects.filter(
                content_type=committee_content_type, object_id=committee.id
            ).first()

            if not context:
                self.stdout.write(
                    self.style.WARNING(f"No context found for committee {committee.key}")
                )
                continue

            prose_content, metadata_content = extract_committee_content(committee)
            all_chunk_texts = []

            if metadata_content.strip():
                all_chunk_texts.append(metadata_content)

            if prose_content.strip():
                prose_chunks = Chunk.split_text(prose_content)
                all_chunk_texts.extend(prose_chunks)

            if not all_chunk_texts:
                self.stdout.write(f"No content to chunk for committee {committee.key}")
                continue

            if chunks := create_chunks_and_embeddings(
                chunk_texts=all_chunk_texts,
                context=context,
                openai_client=self.openai_client,
                save=False,
            ):
                batch_chunks.extend(chunks)
                processed += 1
                self.stdout.write(f"Created {len(chunks)} chunks for {committee.key}")

        if batch_chunks:
            Chunk.bulk_save(batch_chunks)
        return processed
