"""Model definition for the Snapshot class in the OWASP app."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Snapshot(models.Model):
    """Model representing a snapshot of data processing."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        PROCESSING = "processing", _("Processing")
        COMPLETED = "completed", _("Completed")
        ERROR = "error", _("Error")

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    error_message = models.TextField(blank=True)

    # Many-to-Many relationships
    new_chapters = models.ManyToManyField("Chapter", related_name="snapshots", blank=True)
    new_projects = models.ManyToManyField("Project", related_name="snapshots", blank=True)
    new_issues = models.ManyToManyField("GitHubIssue", related_name="snapshots", blank=True)
    new_releases = models.ManyToManyField("GitHubRelease", related_name="snapshots", blank=True)
    new_users = models.ManyToManyField("GitHubUser", related_name="snapshots", blank=True)

    class Meta:
        ordering = ["-start_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["start_at", "end_at"]),
        ]

    def __str__(self):
        """Return a string representation of the snapshot."""
        return f"Snapshot {self.start_at} to {self.end_at} ({self.status})"
