"""Mentorship app experience level."""

from django.db import models


class ExperienceLevel(models.Model):
    """Matching attributes model."""

    class Meta:
        """Model options."""

        abstract = True

    class ExperienceLevelChoices(models.TextChoices):
        """Experience level choices."""

        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"
        EXPERT = "expert", "Expert"

    experience_level = models.CharField(
        max_length=12,
        choices=ExperienceLevelChoices.choices,
        default=ExperienceLevelChoices.BEGINNER,
        verbose_name="Experience level",
    )
