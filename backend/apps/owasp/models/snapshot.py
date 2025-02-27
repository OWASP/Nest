"""OWASP app snapshot models."""

from django.db import models
from django.utils.timezone import now


class Snapshot(models.Model):
    """Model representing a snapshot of data processing."""

    class Meta:
        db_table = "owasp_snapshots"
        verbose_name_plural = "Snapshots"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        ERROR = "error", "Error"

    title = models.CharField(max_length=255, default="")
    key = models.CharField(max_length=7, unique=True)  # Format: YYYY-mm

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(blank=True, default="")

    # Many-to-Many relationships
    new_chapters = models.ManyToManyField("owasp.Chapter", related_name="snapshots", blank=True)
    new_issues = models.ManyToManyField("github.Issue", related_name="snapshots", blank=True)
    new_projects = models.ManyToManyField("owasp.Project", related_name="snapshots", blank=True)
    new_releases = models.ManyToManyField("github.Release", related_name="snapshots", blank=True)
    new_users = models.ManyToManyField("github.User", related_name="snapshots", blank=True)

    def save(self, *args, **kwargs):
        """Automatically set the key in YYYY-mm format before saving."""
        if not self.key:
            self.key = now().strftime("%Y-%m")
        super().save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the snapshot."""
        return f"Snapshot {self.start_at} to {self.end_at} ({self.status})"
