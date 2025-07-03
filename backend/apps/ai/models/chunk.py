"""AI app chunk model."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pgvector.django import VectorField

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.utils import truncate


class Chunk(TimestampedModel):
    """AI Chunk model for storing text chunks with embeddings."""

    class Meta:
        db_table = "ai_chunks"
        verbose_name = "Chunk"
        unique_together = ("content_type", "object_id", "text")

    content_object = GenericForeignKey("content_type", "object_id")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    embedding = VectorField(verbose_name="Embedding", dimensions=1536)
    object_id = models.PositiveIntegerField(default=0)
    text = models.TextField(verbose_name="Text")

    def __str__(self):
        """Human readable representation."""
        content_name = (
            getattr(self.content_object, "name", None)
            or getattr(self.content_object, "key", None)
            or str(self.content_object)
        )
        return (
            f"Chunk {self.id} for {self.content_type.model} {content_name}: "
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
        content_object,
        embedding,
        *,
        save: bool = True,
    ) -> "Chunk | None":
        """Update chunk data.

        Args:
          text (str): The text content of the chunk.
          content_object: The object this chunk belongs to (Message, Chapter, etc.).
          embedding (list): The embedding vector for the chunk.
          save (bool): Whether to save the chunk to the database.

        Returns:
          Chunk: The updated chunk instance or None if it already exists.

        """
        content_type = ContentType.objects.get_for_model(content_object)

        if Chunk.objects.filter(
            content_type=content_type, object_id=content_object.id, text=text
        ).exists():
            return None

        chunk = Chunk(
            content_type=content_type, object_id=content_object.id, text=text, embedding=embedding
        )

        if save:
            chunk.save()

        return chunk
