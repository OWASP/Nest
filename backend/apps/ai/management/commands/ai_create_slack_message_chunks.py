"""A command to create chunks of Slack messages."""

import os

import openai
from django.core.management.base import BaseCommand

from apps.ai.common.create_chunks_and_embeddings import create_chunks_and_embeddings
from apps.ai.models.chunk import Chunk
from apps.slack.models.message import Message


class Command(BaseCommand):
    help = "Create chunks for Slack messages"

    def handle(self, *args, **options):
        if not (openai_api_key := os.getenv("DJANGO_OPEN_AI_SECRET_KEY")):
            self.stdout.write(
                self.style.ERROR("DJANGO_OPEN_AI_SECRET_KEY environment variable not set")
            )
            return

        self.openai_client = openai.OpenAI(api_key=openai_api_key)

        total_messages = Message.objects.count()
        self.stdout.write(f"Found {total_messages} messages to process")

        batch_size = 100
        for offset in range(0, total_messages, batch_size):
            Chunk.bulk_save(
                [
                    chunk
                    for message in Message.objects.all()[offset : offset + batch_size]
                    for chunk in self.handle_chunks(message)
                ]
            )

        self.stdout.write(f"Completed processing all {total_messages} messages")

    def handle_chunks(self, message: Message) -> list[Chunk]:
        """Create chunks from a message."""
        if message.subtype in {"channel_join", "channel_leave"}:
            return []

        if not (chunk_text := Chunk.split_text(message.cleaned_text)):
            self.stdout.write(
                f"No chunks created for message {message.slack_message_id}: "
                f"`{message.cleaned_text}`"
            )
            return []

        return create_chunks_and_embeddings(
            all_chunk_texts=chunk_text,
            content_object=message,
            openai_client=self.openai_client,
        )
