"""OWASP app award model."""

from __future__ import annotations

from django.db import models

from apps.common.models import TimestampedModel


class Award(TimestampedModel):
    """OWASP Award model.

    Represents OWASP awards based on the canonical source at:
    https://github.com/OWASP/owasp.github.io/blob/main/_data/awards.yml
    """

    class Meta:
        db_table = "owasp_awards"
        indexes = [
            models.Index(fields=["category", "year"], name="owasp_award_category_year"),
            models.Index(fields=["-year"], name="owasp_award_year_desc"),
            models.Index(fields=["name"], name="owasp_award_name"),
        ]
        verbose_name = "Award"
        verbose_name_plural = "Awards"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "year", "category"], name="unique_award_name_year_category"
            )
        ]

    # Core fields based on YAML structure
    category = models.CharField(
        verbose_name="Category",
        max_length=100,
        help_text="Award category (e.g., 'WASPY', 'Lifetime Achievement')",
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
        null=True,
        blank=True,
        help_text="Year the award was given (null for category definitions)",
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
    winner_image = models.CharField(
        verbose_name="Winner Image",
        max_length=500,
        blank=True,
        default="",
        help_text="Path to winner's image",
    )

    # Award type from YAML (category or award)
    award_type = models.CharField(
        verbose_name="Award Type",
        max_length=20,
        choices=[
            ("category", "Category"),
            ("award", "Award"),
        ],
        default="award",
        help_text="Type of entry: category definition or individual award",
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

    def __str__(self) -> str:
        """Return string representation of the award."""
        if self.award_type == "category":
            return f"{self.name} (Category)"

        if self.winner_name:
            return f"{self.name} - {self.winner_name} ({self.year})"

        return f"{self.name} ({self.year})"

    @property
    def is_category(self) -> bool:
        """Check if this is a category definition."""
        return self.award_type == "category"

    @property
    def is_award(self) -> bool:
        """Check if this is an individual award."""
        return self.award_type == "award"

    @property
    def display_name(self) -> str:
        """Get display name for the award."""
        if self.is_category:
            return self.name
        return f"{self.name} ({self.year})"

    @classmethod
    def get_waspy_award_winners(cls):
        """Get all users who have won WASPY awards.

        Returns:
            QuerySet of GitHub users who have won WASPY awards

        """
        from apps.github.models.user import User

        return User.objects.filter(awards__category="WASPY", awards__award_type="award").distinct()

    @classmethod
    def get_user_waspy_awards(cls, user):
        """Get all WASPY awards for a specific user.

        Args:
            user: GitHub User instance

        Returns:
            QuerySet of WASPY awards for the user

        """
        return cls.objects.filter(user=user, category="WASPY", award_type="award")

    @staticmethod
    def update_data(award_data: dict, *, save: bool = True):
        """Update award data from YAML structure.

        Args:
            award_data: Dictionary containing award data from YAML
            save: Whether to save the award instance

        Returns:
            Award instance or list of Award instances

        """
        if award_data.get("type") == "category":
            return Award._create_category(award_data, save=save)
        if award_data.get("type") == "award":
            return Award._create_awards_from_winners(award_data, save=save)
        return None

    @staticmethod
    def _create_category(category_data: dict, *, save: bool = True):
        """Create or update a category award."""
        name = category_data.get("title", "")
        description = category_data.get("description", "")

        award, created = (
            Award.objects.get_or_create(
                name=name,
                award_type="category",
                defaults={
                    "category": name,
                    "description": description,
                },
            )
            if save
            else (
                Award(
                    name=name,
                    category=name,
                    award_type="category",
                    description=description,
                ),
                True,
            )
        )

        if not created and save:
            award.description = description
            award.save(update_fields=["description", "nest_updated_at"])

        return award

    @staticmethod
    def _create_awards_from_winners(award_data: dict, *, save: bool = True):
        """Create award instances for each winner."""
        awards = []
        award_name = award_data.get("title", "")
        category = award_data.get("category", "")
        year = award_data.get("year")
        winners = award_data.get("winners", [])

        for winner_data in winners:
            winner_name = winner_data.get("name", "").strip()
            if not winner_name:
                continue

            award_defaults = {
                "award_type": "award",
                "description": "",
                "winner_info": winner_data.get("info", ""),
                "winner_image": winner_data.get("image", ""),
            }

            if save:
                award, created = Award.objects.get_or_create(
                    name=award_name,
                    category=category,
                    year=year,
                    winner_name=winner_name,
                    defaults=award_defaults,
                )
                if not created:
                    # Update existing award
                    for field, value in award_defaults.items():
                        setattr(award, field, value)
                    award.save()
            else:
                award = Award(
                    name=award_name,
                    category=category,
                    year=year,
                    winner_name=winner_name,
                    **award_defaults,
                )

            awards.append(award)

        return awards
