"""OWASP app snapshot models."""

from django.db import models
from django.utils.timezone import now


class Snapshot(models.Model):
    """Model representing a snapshot of data processing."""

    class Meta:
        """Model options."""

        db_table = "owasp_snapshots"
        verbose_name_plural = "Snapshots"

        indexes = [
            models.Index(fields=["-created_at"], name="owasp_snapshot_created_at_idx"),
            models.Index(fields=["key", "status"], name="owasp_snapshot_key_status_idx"),
        ]

    class Status(models.TextChoices):
        """Snapshot processing status choices."""

        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        ERROR = "error", "Error"

    class Frequency(models.TextChoices):
        """Snapshot frequency choices."""

        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"

    title = models.CharField(max_length=255, default="")
    key = models.CharField(max_length=10, unique=True, blank=True)
    frequency = models.CharField(
        max_length=10,
        choices=Frequency.choices,
        default=Frequency.WEEKLY,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(blank=True, default="")

    # Many-to-Many relationships
    chapters = models.ManyToManyField("owasp.Chapter", related_name="snapshots", blank=True)
    events = models.ManyToManyField("owasp.Event", related_name="snapshots", blank=True)
    issues = models.ManyToManyField("github.Issue", related_name="snapshots", blank=True)
    posts = models.ManyToManyField("owasp.Post", related_name="snapshots", blank=True)
    projects = models.ManyToManyField("owasp.Project", related_name="snapshots", blank=True)
    pull_requests = models.ManyToManyField(
        "github.PullRequest", related_name="snapshots", blank=True
    )
    releases = models.ManyToManyField("github.Release", related_name="snapshots", blank=True)
    users = models.ManyToManyField("github.User", related_name="snapshots", blank=True)

    def __str__(self):
        """Return a string representation of the snapshot."""
        return self.title

    @property
    def chapters_count(self) -> int:
        """Return the count of chapters."""
        return self.chapters.count()

    @property
    def events_count(self) -> int:
        """Return the count of events."""
        return self.events.count()

    @property
    def issues_count(self) -> int:
        """Return the count of issues."""
        return self.issues.count()

    @property
    def posts_count(self) -> int:
        """Return the count of posts."""
        return self.posts.count()

    @property
    def projects_count(self) -> int:
        """Return the count of projects."""
        return self.projects.count()

    @property
    def pull_requests_count(self) -> int:
        """Return the count of pull requests."""
        return self.pull_requests.count()

    @property
    def releases_count(self) -> int:
        """Return the count of releases."""
        return self.releases.count()

    @property
    def users_count(self) -> int:
        """Return the count of users."""
        return self.users.count()

    def save(self, *args, **kwargs) -> None:
        """Save the snapshot instance."""
        if not self.key:  # automatically set the key
            reference_dt = self.start_at or now()
            if self.frequency == self.Frequency.WEEKLY:
                iso_year, iso_week, _ = reference_dt.isocalendar()
                self.key = f"{iso_year}-W{iso_week:02d}"
            elif self.frequency == self.Frequency.MONTHLY:
                self.key = reference_dt.strftime("%Y-%m")
            else:
                msg = f"Unsupported snapshot frequency: {self.frequency}"
                raise ValueError(msg)

        super().save(*args, **kwargs)
