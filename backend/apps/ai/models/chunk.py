"""AI app chunk model."""

from django.db import models
# Prefer langchain's text splitter when available; otherwise provide a local fallback
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore
except Exception:
    class RecursiveCharacterTextSplitter:
        """Local fallback splitter used in tests and when langchain isn't installed."""

        def __init__(self, chunk_size=200, chunk_overlap=20, length_function=len, separators=None):
            self.chunk_size = chunk_size
            self.chunk_overlap = chunk_overlap
            self.length_function = length_function
            self.separators = separators or ["\n\n", "\n", " ", ""]

        def split_text(self, text: str) -> list[str]:
            """Simple fixed-size splitting with overlap as a lightweight fallback."""
            if not text:
                return []
            out: list[str] = []
            start = 0
            text_len = len(text)
            while start < text_len:
                end = min(text_len, start + self.chunk_size)
                out.append(text[start:end])
                # move start forward but keep overlap
                next_start = end - self.chunk_overlap
                start = next_start if next_start > start else end
            return out

from pgvector.django import VectorField

from apps.ai.models.context import Context
from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.utils import truncate


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

        """
        if Chunk.objects.filter(context=context, text=text).exists():
            return None

        chunk = Chunk(text=text, embedding=embedding, context=context)

        if save:
            chunk.save()

        return chunk
