"""OWASP app snapshot feedback model."""

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.nest.models import User
from apps.owasp.models.snapshot import Snapshot

MAX_RATING = 5
MIN_RATING = 1


class SnapshotFeedback(models.Model):
    """Model representing a community member's feedback on a snapshot.

    Each user may leave at most one feedback entry per snapshot, consisting of a
    required 1-5 star rating and an optional free-form comment.
    """

    class Meta:
        """Model options."""

        db_table = "owasp_snapshot_feedback"
        verbose_name_plural = "Snapshot Feedback"
        constraints = [
            models.UniqueConstraint(
                fields=["snapshot", "user"],
                name="unique_snapshot_user_feedback",
            ),
        ]
        indexes = [
            models.Index(fields=["snapshot", "-created_at"], name="owasp_feedback_snapshot_idx"),
        ]

    snapshot = models.ForeignKey(
        Snapshot,
        on_delete=models.CASCADE,
        related_name="feedback",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="snapshot_feedback",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_RATING),
            MaxValueValidator(MAX_RATING),
        ],
    )
    comment = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a string representation."""
        return f"{self.user} — {self.snapshot} ({self.rating}/{MAX_RATING})"

    @classmethod
    def submit(cls, *, snapshot, user, rating, comment=""):
        """Create or update feedback. Returns (instance, created)."""
        comment = comment or ""
        if not isinstance(rating, (int, float)):
            raise ValidationError({"rating": "Rating must be a number."})
        rating_field = cls._meta.get_field("rating")
        for validator in rating_field.validators:
            validator(rating)

        return cls.objects.update_or_create(
            snapshot=snapshot,
            user=user,
            defaults={
                "comment": comment,
                "rating": rating,
            },
        )
