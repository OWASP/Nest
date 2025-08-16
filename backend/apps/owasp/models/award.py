"""OWASP app award model."""

from __future__ import annotations

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel


class Award(BulkSaveModel, TimestampedModel):
    """OWASP Award model.

    Represents OWASP awards based on the canonical source at:
    https://github.com/OWASP/owasp.github.io/blob/main/_data/awards.yml
    """

    class Category(models.TextChoices):
        WASPY = "WASPY", "WASPY"
        DISTINGUISHED_LIFETIME = (
            "Distinguished Lifetime Memberships",
            "Distinguished Lifetime Memberships",
        )

    class Meta:
        db_table = "owasp_awards"
        verbose_name = "Award"
        verbose_name_plural = "Awards"

    # Core fields based on YAML structure
    category = models.CharField(
        verbose_name="Category",
        max_length=100,
        choices=Category.choices,
        help_text="Award category (e.g., 'WASPY', 'Distinguished Lifetime Memberships')",
    )
    name = models.CharField(
        verbose_name="Name",
        max_length=200,
        help_text="Award name/title (e.g., 'Event Person of the Year')",
    )
    description = models.TextField(
        verbose_name="Description", blank=True, default="", help_text="Award description"
    )
    year = models.IntegerField(
        verbose_name="Year",
        help_text="Year the award was given",
    )

    # Winner information
    winner_name = models.CharField(
        verbose_name="Winner Name",
        max_length=200,
        blank=True,
        default="",
        help_text="Name of the award recipient",
    )
    winner_info = models.TextField(
        verbose_name="Winner Information",
        blank=True,
        default="",
        help_text="Detailed information about the winner",
    )
    winner_image_url = models.URLField(
        verbose_name="Winner Image URL",
        blank=True,
        default="",
        help_text="URL to winner's image",
    )

    # Optional foreign key to User model
    user = models.ForeignKey(
        "github.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="awards",
        verbose_name="User",
        help_text="Associated GitHub user (if matched)",
    )
    is_reviewed = models.BooleanField(
        verbose_name="Is Reviewed",
        default=False,
        help_text="Whether the user matching has been verified by a human",
    )

    def __str__(self) -> str:
        """Return string representation of the award."""
        if self.winner_name:
            return f"{self.name} - {self.winner_name} ({self.year})"
        return f"{self.name} ({self.year})"

    @property
    def display_name(self) -> str:
        """Get display name for the award."""
        return f"{self.name} ({self.year})"

    @classmethod
    def get_waspy_award_winners(cls):
        """Get all users who have won WASPY awards.

        Returns:
            QuerySet of GitHub users who have won WASPY awards

        """
        from apps.github.models.user import User

        return User.objects.filter(awards__category=cls.Category.WASPY).distinct()

    @classmethod
    def get_user_waspy_awards(cls, user):
        """Get all WASPY awards for a specific user.

        Args:
            user: GitHub User instance

        Returns:
            QuerySet of WASPY awards for the user

        """
        return cls.objects.filter(user=user, category=cls.Category.WASPY)

    @staticmethod
    def bulk_save(awards, fields=None) -> None:  # type: ignore[override]
        """Bulk save awards."""
        BulkSaveModel.bulk_save(Award, awards, fields=fields)

    @staticmethod
    def update_data(award_data: dict, *, save: bool = True) -> Award:
        """Update award data.

        Args:
            award_data: Dictionary containing single award winner data
            save: Whether to save the award instance

        Returns:
            Award instance

        """
        # Create unique identifier for get_or_create
        name = award_data.get("title", "")
        category = award_data.get("category", "")
        year = award_data.get("year")
        winner_name = award_data.get("name", "").strip()

        try:
            award = Award.objects.get(
                name=name,
                category=category,
                year=year,
                winner_name=winner_name,
            )
        except Award.DoesNotExist:
            award = Award(
                name=name,
                category=category,
                year=year,
                winner_name=winner_name,
            )

        award.from_dict(award_data)
        if save:
            award.save()

        return award

    def from_dict(self, data: dict) -> None:
        """Update instance based on dict data.

        Args:
            data: Dictionary containing award data

        """
        fields = {
            "description": data.get("description", ""),
            "winner_info": data.get("info", ""),
            "winner_image_url": data.get("image", ""),
        }

        for key, value in fields.items():
            setattr(self, key, value)
