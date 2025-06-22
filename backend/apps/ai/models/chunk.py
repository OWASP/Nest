"""Slack app chunk model."""

from django.db import models
from pgvector.django import VectorField

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.utils import truncate
from apps.slack.models.message import Message


class Chunk(TimestampedModel):
    """Slack Chunk model."""

    class Meta:
        db_table = "slack_chunks"
        verbose_name = "Chunks"
        unique_together = ("message", "chunk_text")

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="chunks")
    chunk_text = models.TextField(verbose_name="Chunk Text")
    embedding = VectorField(verbose_name="Chunk Embedding", dimensions=1536)

    def __str__(self):
        """Human readable representation."""
        text_preview = truncate(self.chunk_text, 50)
        return f"Chunk {self.id} for Message {self.message.slack_message_id}: {text_preview}"

    def from_chunk(self, chunk_text: str, message: Message, embedding=None) -> None:
        """Update instance based on chunk data."""
        self.chunk_text = chunk_text
        self.message = message
        self.embedding = embedding

    @staticmethod
    def bulk_save(chunks, fields=None):
        """Bulk save chunks."""
        chunks = [chunk for chunk in chunks if chunk is not None]
        if chunks:
            BulkSaveModel.bulk_save(Chunk, chunks, fields=fields)

    @staticmethod
    def update_data(
        chunk_text: str,
        message: Message,
        embedding,
        *,
        save: bool = True,
    ) -> "Chunk | None":
        """Update chunk data.

        Args:
          chunk_text (str): The text content of the chunk.
          message (Message): The message this chunk belongs to.
          embedding (list): The embedding vector for the chunk.
          save (bool): Whether to save the chunk to the database.

        Returns:
          Chunk: The updated chunk instance.

        """
        if Chunk.objects.filter(message=message, chunk_text=chunk_text).exists():
            return None

        chunk = Chunk(message=message)
        chunk.from_chunk(chunk_text, message, embedding)

        if save:
            chunk.save()

        return chunk
