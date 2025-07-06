"""A command to create chunks of Slack messages."""

import os
import time
from datetime import UTC, datetime, timedelta

import openai
from django.core.management.base import BaseCommand

from apps.ai.common.constants import (
    DEFAULT_LAST_REQUEST_OFFSET_SECONDS,
    MIN_REQUEST_INTERVAL_SECONDS,
)
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
                    for chunk in self.create_chunks(message)
                ]
            )

        self.stdout.write(f"Completed processing all {total_messages} messages")

    def create_chunks(self, message: Message) -> list[Chunk]:
        """Create chunks from a message."""
        if message.subtype in {"channel_join", "channel_leave"}:
            return []

        if not (chunk_text := Chunk.split_text(message.cleaned_text)):
            self.stdout.write(
                f"No chunks created for message {message.slack_message_id}: "
                f"`{message.cleaned_text}`"
            )
            return []

        try:
            time_since_last_request = datetime.now(UTC) - getattr(
                self,
                "last_request_time",
                datetime.now(UTC) - timedelta(seconds=DEFAULT_LAST_REQUEST_OFFSET_SECONDS),
            )

            if time_since_last_request < timedelta(seconds=MIN_REQUEST_INTERVAL_SECONDS):
                time.sleep(MIN_REQUEST_INTERVAL_SECONDS - time_since_last_request.total_seconds())

            response = self.openai_client.embeddings.create(
                input=chunk_text,
                model="text-embedding-3-small",
            )
            self.last_request_time = datetime.now(UTC)

            return [
                chunk
                for text, embedding in zip(
                    chunk_text,
                    [d.embedding for d in response.data],  # Embedding data from OpenAI response.
                    strict=True,
                )
                if (
                    chunk := Chunk.update_data(
                        text=text,
                        content_object=message,
                        embedding=embedding,
                        save=False,
                    )
                )
            ]
        except openai.OpenAIError as e:
            self.stdout.write(
                self.style.ERROR(f"OpenAI API error for message {message.slack_message_id}: {e}")
            )
            return []
