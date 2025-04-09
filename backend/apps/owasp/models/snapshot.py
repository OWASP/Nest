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
    key = models.CharField(max_length=10, unique=True, blank=True)

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

    def __str__(self):
        """Return a string representation of the snapshot."""
        return self.title

    def save(self, *args, **kwargs):
        """Save the snapshot instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        if not self.key:  # automatically set the key
            self.key = now().strftime("%Y-%m")

        super().save(*args, **kwargs)

    def generate_summary(self):
        """Generate a brief summary of the snapshot contents."""
        parts = []

        if self.new_chapters.exists():
            parts.append(f"{self.new_chapters.count()} chapters")
        if self.new_issues.exists():
            parts.append(f"{self.new_issues.count()} issues")
        if self.new_projects.exists():
            parts.append(f"{self.new_projects.count()} projects")
        if self.new_releases.exists():
            parts.append(f"{self.new_releases.count()} releases")
        if self.new_users.exists():
            parts.append(f"{self.new_users.count()} users")

        if parts:
            return "Added: " + ", ".join(parts)
        return "No new entities added in this snapshot."
