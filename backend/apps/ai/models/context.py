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
