"""Feedback model for storing feedback."""

from django.db import models

from apps.common.models import TimestampedModel


class Feedback(TimestampedModel):
    """Model for storing feedback."""

    name = models.CharField(max_length=100, default="Anonymous")
    email = models.EmailField(default="Anonymous")
    message = models.TextField()
    is_anonymous = models.BooleanField(default=True)
    is_nestbot = models.BooleanField(default=False)
    s3_file_path = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Feedbacks"

    def __str__(self):
        """Return string representation of the Feedback model."""
        return f"{self.name} - {self.created_at}"
