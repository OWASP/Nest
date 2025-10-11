"""OWASP app Board of Directors models."""

from django.db import models


class BoardOfDirectors(models.Model):
    """Model representing OWASP Board of Directors."""

    class Meta:
        db_table = "owasp_board_of_directors"
        verbose_name_plural = "Board of Directors"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    year = models.PositiveSmallIntegerField(unique=True)

    def __str__(self):
        """Return a string representation of the Board of Directors."""
        return f"OWASP {self.year} Board of Directors"
