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

    def generate_summary(self, max_examples=2):
        """Generate a snapshot summary with counts and examples."""
        summary_parts = []

        def summarize(queryset, label, example_attr):
            count = queryset.count()
            if count == 0:
                return None
            examples = list(queryset.values_list(example_attr, flat=True)[:max_examples])
            example_str = ", ".join(str(e) for e in examples)
            return f"{count} {label}{'s' if count != 1 else ''} (e.g., {example_str})"

        entities = [
            (self.new_users, "user", "login"),
            (self.new_projects, "project", "name"),
            (self.new_chapters, "chapter", "name"),
            (self.new_issues, "issue", "title"),
            (self.new_releases, "release", "tag_name"),
        ]

        for queryset, label, attr in entities:
            part = summarize(queryset, label, attr)
            if part:
                summary_parts.append(part)

        return (
            "Snapshot Summary: " + "; ".join(summary_parts)
            if summary_parts
            else "No new entities were added."
        )
