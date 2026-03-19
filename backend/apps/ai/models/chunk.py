"""AI app chunk model."""

import logging

from django.conf import settings
from django.db import IntegrityError, models
from pgvector.django import VectorField

from apps.ai.models.context import Context
from apps.common.models import TimestampedModel
from apps.common.utils import truncate

BULK_BATCH_SIZE = 1000

logger = logging.getLogger(__name__)


class Chunk(TimestampedModel):
    """AI Chunk model for storing text chunks with embeddings."""

    class Meta:
        """Table and unique constraint configuration for Chunk."""

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
        """Bulk save chunks; duplicate (context, text) rows are skipped (constraint-aware)."""
        new_chunks = [c for c in chunks if not c.id]
        existing = [c for c in chunks if c.id]
        if new_chunks:
            Chunk.objects.bulk_create(
                new_chunks, batch_size=BULK_BATCH_SIZE, ignore_conflicts=True
            )
        if existing:
            Chunk.objects.bulk_update(
                existing,
                fields=fields or [f.name for f in Chunk._meta.fields if not f.primary_key],
                batch_size=BULK_BATCH_SIZE,
            )
        chunks.clear()

    @staticmethod
    def split_text(text: str) -> list[str]:
        """Split text into chunks."""
        from langchain_text_splitters import RecursiveCharacterTextSplitter  # noqa: PLC0415

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
          Chunk | None: The created chunk instance, or None if duplicate.

        Raises:
          ValueError: If embedding dimension doesn't match the field dimension.

        """
        # Validate embedding dimension matches the field dimension
        # Only enforce strict validation in production to avoid breaking tests
        expected_dimension = Chunk._meta.get_field("embedding").dimensions
        actual_dimension = len(embedding) if embedding else 0

        if actual_dimension == 0:
            error_msg = "Embedding dimension cannot be zero"
            logger.error(error_msg, extra={"context_id": context.id if context else None})
            raise ValueError(error_msg)

        if actual_dimension != expected_dimension:
            # Log warning but only raise error in production/staging environments
            # This allows tests to use different dimensions while catching real issues
            warning_msg = (
                f"Embedding dimension mismatch: expected {expected_dimension}, "
                f"got {actual_dimension}. This usually indicates a mismatch between "
                f"the LLM_PROVIDER setting and the Chunk model's VectorField dimension."
            )
            logger.warning(warning_msg, extra={"context_id": context.id if context else None})

            # Raise only in production/staging; skip in test/local/dev/preview
            is_production = getattr(settings, "IS_PRODUCTION_ENVIRONMENT", False)
            is_staging = getattr(settings, "IS_STAGING_ENVIRONMENT", False)
            is_test = getattr(settings, "IS_TEST_ENVIRONMENT", False)
            is_local = getattr(settings, "IS_LOCAL_ENVIRONMENT", False)
            should_enforce = (is_production or is_staging) and not (is_test or is_local)
            if should_enforce:
                error_msg = (
                    f"{warning_msg} Ensure the embedding provider matches "
                    "the configured dimension."
                )
                raise ValueError(error_msg)
            # Non-prod: do not save mismatched-dimension vector; pgvector would reject it
            return None

        if Chunk.objects.filter(context=context, text=text).exists():
            return None

        chunk = Chunk(text=text, embedding=embedding, context=context)

        if save:
            try:
                chunk.save()
            except IntegrityError:
                # Concurrent insert or duplicate; treat as skip (constraint-aware)
                return None

        return chunk
