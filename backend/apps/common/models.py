"""Common app models."""

from django.db import models


class TimestampedModel(models.Model):
    """Base model with auto created_at and updated_at fields."""

    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
