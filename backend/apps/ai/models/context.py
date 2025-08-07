"""AI app context model."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.common.models import TimestampedModel


class Context(TimestampedModel):
    """Context model for storing generated text and optional relation to OWASP entities."""

    content = models.TextField(verbose_name="Generated Text")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(default=0)
    content_object = GenericForeignKey("content_type", "object_id")
    source = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        db_table = "ai_contexts"
        verbose_name = "Context"
        unique_together = ("content_type", "object_id")

    def __str__(self):
        """Human readable representation."""
        entity = (
            getattr(self.content_object, "name", None)
            or getattr(self.content_object, "key", None)
            or str(self.content_object)
        )
        return (
            f"{self.content_type.model if self.content_type else 'None'} {entity}: "
            f"{self.content[:50]}"
        )

    @staticmethod
    def update_data(
        content: str,
        content_object=None,
        source: str = "",
        *,
        save: bool = True,
    ) -> "Context | None":
        """Update context data.

        Args:
          content (str): The content text of the context.
          content_object: Optional related object (generic foreign key).
          source (str): Source identifier for the context.
          save (bool): Whether to save the context to the database.

        Returns:
          Context: The updated context instance or None if it already exists.

        """
        if content_object:
            content_type = ContentType.objects.get_for_model(content_object)
            object_id = content_object.pk
            if Context.objects.filter(
                content_type=content_type, object_id=object_id, content=content
            ).exists():
                return None
        elif Context.objects.filter(content=content, content_object__isnull=True).exists():
            return None

        context = Context(content=content, content_object=content_object, source=source)

        if save:
            context.save()

        return context
