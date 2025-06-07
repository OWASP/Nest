"""A command to create chunks of Slack messages."""

import os

import openai
from django.core.management.base import BaseCommand
from langchain.text_splitter import RecursiveCharacterTextSplitter

from apps.slack.models.chunk import Chunk
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

        messages = Message.objects.all()
        total_messages = messages.count()
        print(f"Found {total_messages} messages to process")

        all_chunks = []

        for message in messages:
            chunks = self.create_chunks_from_message(message)
            all_chunks.extend(chunks)

        if all_chunks:
            self.stdout.write(f"\nSaving {len(all_chunks)} chunks to database...")
            Chunk.objects.bulk_create(all_chunks)
            self.stdout.write(f"Successfully saved {len(all_chunks)} chunks")
        else:
            self.stdout.write("No chunks were created")

    def create_chunks_from_message(self, message: Message) -> list[Chunk]:
        chunk_texts = self.split_message_text(message.text)

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
                Chunk(message=message, chunk_text=text, embedding=embedding)
                for text, embedding in zip(chunk_texts, embeddings, strict=True)
            ]
        except openai.error.OpenAIError as e:
            self.stdout.write(
                self.style.ERROR(f"OpenAI API error for message {message.slack_message_id}: {e}")
            )
            return []

    def split_message_text(self, message_text: str) -> list[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=40,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )
        return splitter.split_text(message_text)
