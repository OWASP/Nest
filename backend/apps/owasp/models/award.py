"""OWASP app award model."""

from __future__ import annotations

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel


class Award(BulkSaveModel, TimestampedModel):
    """Award model."""

    class Meta:
        db_table = "owasp_awards"
        indexes = [
            models.Index(fields=["-year"], name="award_year_desc_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "name", "year"],
                name="uniq_award_cat_name_year",
            ),
        ]
        verbose_name_plural = "Awards"

    category = models.CharField(verbose_name="Category", max_length=100)
    name = models.CharField(verbose_name="Name", max_length=255)
    description = models.TextField(verbose_name="Description", blank=True, default="")
    year = models.IntegerField(verbose_name="Year")
    is_reviewed = models.BooleanField(
        verbose_name="Is reviewed",
        default=False,
        help_text="Indicates if the user matching has been reviewed by a human.",
    )

    # FKs.
    user = models.ForeignKey(
        "github.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="awards",
        verbose_name="User",
    )

    def __str__(self) -> str:
        """Award human readable representation."""
        return f"{self.name} ({self.year})"

    @staticmethod
    def bulk_save(  # type: ignore[override]
        awards: list,
        fields: tuple[str, ...] | None = None,
    ) -> None:
        """Bulk save awards.

        Args:
            awards (list): A list of Award instances to be saved.
            fields (tuple, optional): A tuple of fields to update during the bulk save.

        Returns:
            None

        """
        BulkSaveModel.bulk_save(Award, awards, fields=fields)
