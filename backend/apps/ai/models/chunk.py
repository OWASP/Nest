"""Slack app chunk model."""

from django.db import models
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pgvector.django import VectorField

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.utils import truncate
from apps.slack.models.message import Message


class Chunk(TimestampedModel):
    """Slack Chunk model."""

    class Meta:
        db_table = "ai_chunks"
        verbose_name = "Chunk"
        unique_together = ("message", "text")

    embedding = VectorField(verbose_name="Embedding", dimensions=1536)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="chunks")
    text = models.TextField(verbose_name="Text")

    def __str__(self):
        """Human readable representation."""
        return (
            f"Chunk {self.id} for Message {self.message.slack_message_id}: "
            f"{truncate(self.text, 50)}"
        )

    @staticmethod
    def bulk_save(chunks, fields=None):
        """Bulk save chunks."""
        BulkSaveModel.bulk_save(Chunk, chunks, fields=fields)

    @staticmethod
    def split_text(text: str) -> list[str]:
        """Split text into chunks."""
        return RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=40,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        ).split_text(text)

    @staticmethod
    def update_data(
        text: str,
        message: Message,
        embedding,
        *,
        save: bool = True,
    ) -> "Chunk | None":
        """Update chunk data.

        Args:
          text (str): The text content of the chunk.
          message (Message): The message this chunk belongs to.
          embedding (list): The embedding vector for the chunk.
          save (bool): Whether to save the chunk to the database.

        Returns:
          Chunk: The updated chunk instance.

        """
        if Chunk.objects.filter(message=message, text=text).exists():
            return None

        chunk = Chunk(message=message, text=text, embedding=embedding)

        if save:
            chunk.save()

        return chunk
