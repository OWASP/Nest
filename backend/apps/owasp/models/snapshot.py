"""OWASP app snapshot models."""

from django.db import models
from django.utils.timezone import now


class Snapshot(models.Model):
    """Model representing a snapshot of data processing."""

    class Meta:
        db_table = "owasp_snapshots"
        verbose_name_plural = "Snapshots"

        indexes = [
            models.Index(fields=["-created_at"], name="owasp_snapshot_created_at_idx"),
            models.Index(fields=["key", "status"], name="owasp_snapshot_key_status_idx"),
        ]

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

    @property
    def new_chapters_count(self) -> int:
        """Return the count of new chapters."""
        return self.new_chapters.count()

    @property
    def new_issues_count(self) -> int:
        """Return the count of new issues."""
        return self.new_issues.count()

    @property
    def new_projects_count(self) -> int:
        """Return the count of new projects."""
        return self.new_projects.count()

    @property
    def new_releases_count(self) -> int:
        """Return the count of new releases."""
        return self.new_releases.count()

    @property
    def new_users_count(self) -> int:
        """Return the count of new users."""
        return self.new_users.count()

    def save(self, *args, **kwargs) -> None:
        """Save the snapshot instance."""
        if not self.key:  # automatically set the key
            self.key = now().strftime("%Y-%m")

        super().save(*args, **kwargs)
