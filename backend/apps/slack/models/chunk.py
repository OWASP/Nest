"""Slack app chunk model."""

from django.db import models
from apps.common.models import TimestampedModel
from apps.slack.models.message import Message
from pgvector.django import VectorField
from apps.common.utils import truncate

class Chunk(TimestampedModel):
    """Slack Chunk model."""

    class Meta:
        db_table = "slack_chunks"
        verbose_name = "Chunks"

    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="chunks"
    )
    chunk_text = models.TextField(verbose_name="Chunk Text")
    embedding = VectorField(verbose_name="Chunk Embedding", dimensions=1536)


    def __str__(self):
        """Human readable representation."""
        text_preview = truncate(self.chunk_text, 50)
        return f"Chunk {self.id} for Message {self.message.slack_message_id}: {text_preview}"

    @staticmethod
    def bulk_save(chunks, fields=None):
        """Bulk save chunks."""
        from apps.common.models import BulkSaveModel
        BulkSaveModel.bulk_save(Chunk, chunks, fields=fields)

    @staticmethod
    def update_data(chunk_text: str, message: Message, embedding=None, *, save: bool = True) -> "Chunk":
        """Create or update chunk data."""
        chunk = Chunk(
            message=message,
            chunk_text=chunk_text,
            embedding=embedding
        )
        
        if save:
            chunk.save()
        
        return chunk