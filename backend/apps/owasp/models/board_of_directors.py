"""OWASP app Board of Directors models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.db import models

if TYPE_CHECKING:
    from django.db.models import QuerySet

from apps.owasp.models.entity_member import EntityMember


class BoardOfDirectors(models.Model):
    """Model representing OWASP Board of Directors."""

    class Meta:
        """Model options."""

        db_table = "owasp_board_of_directors"
        verbose_name_plural = "Board of Directors"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviews_threshold = models.PositiveSmallIntegerField(
        default=3,
        verbose_name="Reviews Threshold",
        help_text="Minimum number of reviews required to finalize a claim.",
    )
    year = models.PositiveSmallIntegerField(unique=True)

    def __str__(self):
        """Return a string representation of the Board of Directors."""
        return f"OWASP {self.year} Board of Directors"

    @property
    def owasp_url(self) -> str:
        """Return the OWASP Board election URL for this year.

        Returns:
            str: The URL to the board election page.

        """
        return f"https://board.owasp.org/elections/{self.year}_elections"

    def get_candidate(self, login: str) -> EntityMember | None:
        """Return the candidate for this board election.

        Args:
            login (str): the login of the user.

        Returns:
            EntityMember | None: The candidate if found, None otherwise.

        """
        return self.get_candidates().filter(member__login=login).first()

    def get_candidates(self) -> QuerySet[EntityMember]:
        """Return all candidates for this board election."""
        return EntityMember.objects.filter(
            entity_type=ContentType.objects.get_for_model(self.__class__),
            entity_id=self.id,
            role=EntityMember.Role.CANDIDATE,
            is_active=True,
            is_reviewed=True,
        ).order_by("member_name")

    def get_members(self) -> QuerySet[EntityMember]:
        """Return all members of this board."""
        return EntityMember.objects.filter(
            entity_type=ContentType.objects.get_for_model(self.__class__),
            entity_id=self.id,
            role=EntityMember.Role.MEMBER,
            is_active=True,
            is_reviewed=True,
        ).order_by("member_name")
