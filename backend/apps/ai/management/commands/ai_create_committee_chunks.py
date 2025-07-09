"""A command to create chunks of OWASP committee data for RAG."""

import os

import openai
from django.core.management.base import BaseCommand

from apps.ai.common.constants import DELIMITER
from apps.ai.common.utils import create_chunks_and_embeddings
from apps.ai.models.chunk import Chunk
from apps.owasp.models.committee import Committee


class Command(BaseCommand):
    help = "Create chunks for OWASP committee data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--committee",
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

        if committee := options["committee"]:
            queryset = Committee.objects.filter(key=committee)
        elif options["all"]:
            queryset = Committee.objects.all()
        else:
            queryset = Committee.objects.filter(is_active=True)

        if not (total_committees := queryset.count()):
            self.stdout.write("No committees found to process")
            return

        self.stdout.write(f"Found {total_committees} committees to process")

        batch_size = options["batch_size"]
        for offset in range(0, total_committees, batch_size):
            batch_committees = queryset[offset : offset + batch_size]

            batch_chunks = []
            for committee in batch_committees:
                batch_chunks.extend(self.handle_chunks(committee))

            if batch_chunks:
                Chunk.bulk_save(batch_chunks)
                self.stdout.write(f"Saved {len(batch_chunks)} chunks")

        self.stdout.write(f"Completed processing all {total_committees} committees")

    def handle_chunks(self, committee: Committee) -> list[Chunk]:
        """Create chunks from a committee's data."""
        prose_content, metadata_content = self.extract_committee_content(committee)

        all_chunk_texts = []

        if metadata_content.strip():
            all_chunk_texts.append(metadata_content)

        if prose_content.strip():
            all_chunk_texts.extend(Chunk.split_text(prose_content))

        if not all_chunk_texts:
            self.stdout.write(f"No content to chunk for committee {committee.key}")
            return []

        return create_chunks_and_embeddings(
            all_chunk_texts=all_chunk_texts,
            content_object=committee,
            openai_client=self.openai_client,
        )

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
