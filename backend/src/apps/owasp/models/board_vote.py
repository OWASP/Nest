"""OWASP app board vote model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.owasp.models.board_motion import BoardMotion
from apps.owasp.models.entity_member import EntityMember


class BoardVote(TimestampedModel):
    """Board vote model."""

    class Result(models.TextChoices):
        """Board vote result choices."""

        DEFERRED = "deferred", "Deferred"
        FAILED = "failed", "Failed"
        PASSED = "passed", "Passed"
        TABLED = "tabled", "Tabled"
        WITHDRAWN = "withdrawn", "Withdrawn"

    class Type(models.TextChoices):
        """Board vote type choices."""

        E_VOTE = "e_vote", "E-Vote"
        VOTE = "vote", "Vote"

    class Meta:
        """Model options."""

        db_table = "owasp_board_votes"
        verbose_name_plural = "Board Votes"

    metadata = models.JSONField(default=dict, blank=True)
    result = models.CharField(max_length=9, choices=Result.choices)
    tally = models.CharField(max_length=255, blank=True, default="")
    type = models.CharField(max_length=6, choices=Type.choices, default=Type.VOTE)

    abstain = models.ManyToManyField(EntityMember, blank=True, related_name="+")
    against = models.ManyToManyField(EntityMember, blank=True, related_name="+")
    in_favor = models.ManyToManyField(EntityMember, blank=True, related_name="+")
    recused = models.ManyToManyField(EntityMember, blank=True, related_name="+")

    motion = models.ForeignKey(
        BoardMotion,
        on_delete=models.CASCADE,
        related_name="votes",
    )

    def __str__(self) -> str:
        """Return the board vote human-readable representation."""
        return f"Vote ({self.get_result_display()}): {self.tally or 'n/a'}"
