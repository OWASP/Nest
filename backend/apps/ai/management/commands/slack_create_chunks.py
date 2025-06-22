"""A command to create chunks of Slack messages."""

import os
import re

import openai
from django.core.management.base import BaseCommand
from langchain.text_splitter import RecursiveCharacterTextSplitter

from apps.ai.models.chunk import Chunk
from apps.slack.models.message import Message


class Command(BaseCommand):
    help = "Create chunks for Slack messages"

    def handle(self, *args, **options):
        openai_api_key = os.getenv("DJANGO_OPEN_AI_SECRET_KEY")

        if not openai_api_key:
            self.stdout.write(
                self.style.ERROR("DJANGO_OPEN_AI_SECRET_KEY environment variable not set")
            )
            return

        self.openai_client = openai.OpenAI(api_key=openai_api_key)

        total_messages = Message.objects.count()
        self.stdout.write(f"Found {total_messages} messages to process")

        batch_size = 1000
        processed_count = 0

        for offset in range(0, total_messages, batch_size):
            batch_messages = Message.objects.all()[offset : offset + batch_size]
            batch_chunks = []

            for message in batch_messages:
                cleaned_text = self.clean_message_text(message.raw_data.get("text", ""))
                chunks = self.create_chunks_from_message(message, cleaned_text)
                batch_chunks.extend(chunks)

            if batch_chunks:
                Chunk.bulk_save(batch_chunks)

            processed_count += len(batch_messages)

        self.stdout.write(f"Completed processing all {total_messages} messages")

    def create_chunks_from_message(
        self, message: Message, cleaned_text: str
    ) -> list[Chunk | None]:
        """Create chunks from a message."""
        if message.raw_data.get("subtype") in ["channel_join", "channel_leave"]:
            return []

        chunk_texts = self.split_message_text(cleaned_text)

        if not chunk_texts:
            self.stdout.write(
                f"No chunks created for message {message.slack_message_id} - text too short"
            )
            return []

        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small", input=chunk_texts
            )
            embeddings = [d.embedding for d in response.data]
            return [
                Chunk.update_data(
                    chunk_text=text,
                    message=message,
                    embedding=embedding,
                    save=False,
                )
                for text, embedding in zip(chunk_texts, embeddings, strict=True)
            ]
        except openai.error.OpenAIError as e:
            self.stdout.write(
                self.style.ERROR(f"OpenAI API error for message {message.slack_message_id}: {e}")
            )
            return []

    def split_message_text(self, message_text: str) -> list[str]:
        """Split message text into chunks."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=40,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )
        return splitter.split_text(message_text)

    def clean_message_text(self, message_text: str) -> str:
        """Clean message text by removing emojis and other noise while preserving context."""
        if not message_text:
            return ""

        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"
            "\U0001f300-\U0001f5ff"
            "\U0001f680-\U0001f6ff"
            "\U0001f1e0-\U0001f1ff"
            "\U00002500-\U00002bef"
            "\U00002702-\U000027b0"
            "\U000024c2-\U0001f251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2640-\u2642"
            "\u2600-\u2b55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f"
            "\u3030"
            "]+",
            flags=re.UNICODE,
        )

        cleaned_text = re.sub(r"<@U[A-Z0-9]+>", "", message_text)
        cleaned_text = re.sub(r"<https?://[^>]+>", "", cleaned_text)
        cleaned_text = re.sub(r":\w+:", "", cleaned_text)
        cleaned_text = emoji_pattern.sub("", cleaned_text)
        cleaned_text = re.sub(r"\s+", " ", cleaned_text)

        return cleaned_text.strip()
