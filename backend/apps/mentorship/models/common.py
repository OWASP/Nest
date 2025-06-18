"""Common models and choices for the mentorship app."""

from django.db import models


class MenteeLevelChoices(models.TextChoices):
    """Skill level choices for mentees."""

    BEGINNER = "beginner", "Beginner"
    INTERMEDIATE = "intermediate", "Intermediate"
    ADVANCED = "advanced", "Advanced"
