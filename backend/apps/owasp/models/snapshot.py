"""OWASP app snapshot models."""

from django.db import models


class Snapshot(models.Model):
    """Model representing a snapshot of data processing."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        ERROR = "error", "Error"

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    error_message = models.TextField(blank=True, default="")

    # Many-to-Many relationships
    new_chapters = models.ManyToManyField("owasp.Chapter", related_name="snapshots", blank=True)
    new_projects = models.ManyToManyField("owasp.Project", related_name="snapshots", blank=True)
    new_issues = models.ManyToManyField("github.Issue", related_name="snapshots", blank=True)
    new_releases = models.ManyToManyField("github.Release", related_name="snapshots", blank=True)
    new_users = models.ManyToManyField("github.User", related_name="snapshots", blank=True)

    class Meta:
        db_table = "owasp_snapshots"
        verbose_name_plural = "Snapshots"
        ordering = ["-start_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["start_at", "end_at"]),
        ]

    def __str__(self):
        """Return a string representation of the snapshot."""
        return f"Snapshot {self.start_at} to {self.end_at} ({self.status})"
