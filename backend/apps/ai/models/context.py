"""AI app context model."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.common.models import TimestampedModel


class Context(TimestampedModel):
    """Context model for storing generated text related to OWASP entities."""

    content = models.TextField(verbose_name="Generated Text")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    source = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        db_table = "ai_contexts"
        verbose_name = "Context"
        unique_together = ("content_type", "object_id", "content")

    def __str__(self):
        """Human readable representation."""
        entity = (
            getattr(self.content_object, "name", None)
            or getattr(self.content_object, "key", None)
            or str(self.content_object)
        )
        return f"{self.content_type.model} {entity}: {self.content[:50]}"

    @staticmethod
    def update_data(
        content: str,
        content_object,
        source: str = "",
        *,
        save: bool = True,
    ) -> "Context":
        """Retrieve existing or create new context."""
        content_type = ContentType.objects.get_for_model(content_object)
        object_id = content_object.pk
        existing_context = Context.objects.filter(
            content_type=content_type, object_id=object_id, content=content
        ).first()
        if existing_context:
            return existing_context

        context = Context(content=content, content_object=content_object, source=source)

        if save:
            context.save()

        return context
