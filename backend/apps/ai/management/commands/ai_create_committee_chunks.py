"""A command to create chunks of OWASP committee data for RAG."""

import os

import openai
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.ai.common.constants import DELIMITER
from apps.ai.common.utils import create_chunks_and_embeddings, create_context
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

            if options["context"]:
                processed_count += self.process_context_batch(batch_committees)
            elif options["chunks"]:
                processed_count += self.process_chunks_batch(batch_committees)

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed processing {processed_count}/{total_committees} committees"
            )
        )

    def process_context_batch(self, committees: list[Committee]) -> int:
        """Process a batch of committees to create contexts."""
        processed = 0

        for committee in committees:
            prose_content, metadata_content = self.extract_committee_content(committee)
            full_content = (
                f"{metadata_content}\n\n{prose_content}" if metadata_content else prose_content
            )

            if not full_content.strip():
                self.stdout.write(f"No content for committee {committee.key}")
                continue

            if create_context(
                content=full_content, content_object=committee, source="owasp_committee"
            ):
                processed += 1
                self.stdout.write(f"Created context for {committee.key}")
            else:
                self.stdout.write(
                    self.style.ERROR(f"Failed to create context for {committee.key}")
                )
        return processed

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

            prose_content, metadata_content = self.extract_committee_content(committee)
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

    def extract_committee_content(self, committee: Committee) -> tuple[str, str]:
        """Extract structured content from committee data."""
        prose_parts = []
        metadata_parts = []

        if committee.description:
            prose_parts.append(f"Description: {committee.description}")

        if committee.summary:
            prose_parts.append(f"Summary: {committee.summary}")

        if hasattr(committee, "owasp_repository") and committee.owasp_repository:
            repo = committee.owasp_repository
            if repo.description:
                prose_parts.append(f"Repository Description: {repo.description}")
            if repo.topics:
                metadata_parts.append(f"Repository Topics: {', '.join(repo.topics)}")

        if committee.name:
            metadata_parts.append(f"Committee Name: {committee.name}")

        if committee.tags:
            metadata_parts.append(f"Tags: {', '.join(committee.tags)}")

        if committee.topics:
            metadata_parts.append(f"Topics: {', '.join(committee.topics)}")

        if committee.leaders_raw:
            metadata_parts.append(f"Committee Leaders: {', '.join(committee.leaders_raw)}")

        if committee.related_urls:
            valid_urls = [
                url
                for url in committee.related_urls
                if url and url not in (committee.invalid_urls or [])
            ]
            if valid_urls:
                metadata_parts.append(f"Related URLs: {', '.join(valid_urls)}")

        metadata_parts.append(f"Active Committee: {'Yes' if committee.is_active else 'No'}")

        return (
            DELIMITER.join(filter(None, prose_parts)),
            DELIMITER.join(filter(None, metadata_parts)),
        )
