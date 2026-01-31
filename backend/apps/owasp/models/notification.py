"""Notification and Subscription models."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.nest.models import User


class Subscription(models.Model):
    """Model representing a user's subscription to a specific entity."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "owasp_subscriptions"
        unique_together = ("user", "content_type", "object_id")
        indexes = [
            models.Index(fields=["user", "content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.user} -> {self.content_object}"


class Notification(models.Model):
    """Model representing a notification sent to a user."""

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=50)  # e.g., 'snapshot_published', 'release', etc.
    title = models.CharField(max_length=255)
    message = models.TextField()
    related_link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "owasp_notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} -> {self.recipient}"
