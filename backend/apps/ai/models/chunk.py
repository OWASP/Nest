"""AI app chunk model."""

import logging

from django.db import models
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pgvector.django import VectorField

from apps.ai.models.context import Context
from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.utils import truncate

logger = logging.getLogger(__name__)


class Chunk(TimestampedModel):
    """AI Chunk model for storing text chunks with embeddings."""

    class Meta:
        db_table = "ai_chunks"
        verbose_name = "Chunk"
        unique_together = ("context", "text")

    context = models.ForeignKey(Context, on_delete=models.CASCADE, related_name="chunks")
    embedding = VectorField(verbose_name="Embedding", dimensions=1536)
    text = models.TextField(verbose_name="Text")

    def __str__(self):
        """Human readable representation."""
        context_str = str(self.context) if self.context else "No Context"
        return f"Chunk {self.id} for {context_str}: {truncate(self.text, 50)}"

    @staticmethod
    def bulk_save(chunks, fields=None):
        """Bulk save chunks."""
        BulkSaveModel.bulk_save(Chunk, chunks, fields=fields)

    @staticmethod
    def split_text(text: str) -> list[str]:
        """Split text into chunks."""
        return RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=20,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        ).split_text(text)

    @staticmethod
    def update_data(
        text: str,
        embedding,
        context: Context,
        *,
        save: bool = True,
    ) -> "Chunk | None":
        """Update chunk data.

        Args:
          text (str): The text content of the chunk.
          embedding (list): The embedding vector for the chunk.
          context (Context): The context this chunk belongs to.
          save (bool): Whether to save the chunk to the database.

        Returns:
          Chunk: The created chunk instance.

        Raises:
          ValueError: If embedding dimension doesn't match the field dimension.

        """
        # Validate embedding dimension matches the field dimension
        expected_dimension = Chunk._meta.get_field("embedding").dimensions
        actual_dimension = len(embedding) if embedding else 0

        if actual_dimension != expected_dimension:
            error_msg = (
                f"Embedding dimension mismatch: expected {expected_dimension}, "
                f"got {actual_dimension}. This usually indicates a mismatch between "
                f"the LLM_PROVIDER setting and the Chunk model's VectorField dimension. "
                f"Ensure the embedding provider matches the configured dimension."
            )
            logger.error(error_msg, extra={"context_id": context.id if context else None})
            raise ValueError(error_msg)

        if Chunk.objects.filter(context=context, text=text).exists():
            return None

        chunk = Chunk(text=text, embedding=embedding, context=context)

        if save:
            chunk.save()

        return chunk
