"""A command to create chunks of Slack messages."""

import os

import openai
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.ai.common.utils import create_chunks_and_embeddings, create_context
from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context
from apps.slack.models.message import Message


class Command(BaseCommand):
    help = "Create chunks for Slack messages"

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of messages to process in each batch",
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

        queryset = Message.objects.all()
        total_messages = queryset.count()

        if not total_messages:
            self.stdout.write("No messages found to process")
            return

        self.stdout.write(f"Found {total_messages} messages to process")

        batch_size = options["batch_size"]
        processed_count = 0

        for offset in range(0, total_messages, batch_size):
            batch_messages = queryset[offset : offset + batch_size]

            if options["context"]:
                processed_count += self.process_context_batch(batch_messages)
            elif options["chunks"]:
                processed_count += self.process_chunks_batch(batch_messages)

        self.stdout.write(
            self.style.SUCCESS(f"Completed processing {processed_count}/{total_messages} messages")
        )

    def process_context_batch(self, messages: list[Message]) -> int:
        """Process a batch of messages to create contexts."""
        processed = 0

        for message in messages:
            if not message.cleaned_text or not message.cleaned_text.strip():
                continue

            if create_context(
                content=message.cleaned_text,
                content_object=message,
                source="slack_message",
            ):
                processed += 1
                self.stdout.write(f"Created context for message {message.slack_message_id}")
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to create context for message {message.slack_message_id}"
                    )
                )
        return processed

    def process_chunks_batch(self, messages: list[Message]) -> int:
        """Process a batch of messages to create chunks."""
        processed = 0
        batch_chunks = []

        message_content_type = ContentType.objects.get_for_model(Message)

        for message in messages:
            context = Context.objects.filter(
                content_type=message_content_type, object_id=message.id
            ).first()

            if not context:
                self.stdout.write(
                    self.style.WARNING(f"No context found for message {message.slack_message_id}")
                )
                continue

            if not message.cleaned_text or not message.cleaned_text.strip():
                self.stdout.write(f"No content to chunk for message {message.slack_message_id}")
                continue

            chunk_texts = Chunk.split_text(message.cleaned_text)
            if not chunk_texts:
                self.stdout.write(
                    f"No chunks created for message {message.slack_message_id}: "
                    f"`{message.cleaned_text}`"
                )
                continue

            if chunks := create_chunks_and_embeddings(
                chunk_texts=chunk_texts,
                context=context,
                openai_client=self.openai_client,
                save=False,
            ):
                batch_chunks.extend(chunks)
                processed += 1
                self.stdout.write(
                    f"Created {len(chunks)} chunks for message {message.slack_message_id}"
                )

        if batch_chunks:
            Chunk.bulk_save(batch_chunks)
        return processed
