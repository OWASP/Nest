"""OWASP app entity member model."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.github.models.user import User


class EntityMember(models.Model):
    """EntityMember model."""

    class MemberKind(models.TextChoices):
        LEADER = "leader", "Leader"

    class Meta:
        db_table = "owasp_entity_members"
        unique_together = (
            "entity_type",
            "entity_id",
            "member",
            "kind",
        )
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["member"]),
        ]
        verbose_name_plural = "Entity members"

    description = models.TextField(
        blank=True,
        default="",
        help_text="Optional role or description",
    )
    entity = GenericForeignKey("entity_type", "entity_id")
    entity_id = models.PositiveIntegerField()
    entity_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    is_reviewed = models.BooleanField(
        default=False,
        help_text="Indicates if the membership is verified",
    )
    kind = models.CharField(
        max_length=6,
        choices=MemberKind.choices,
        default=MemberKind.LEADER,
    )
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="+",
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order/priority of members",
    )

    def __str__(self):
        """EntityMember human readable representation."""
        return f"{self.member.login} as {self.get_kind_display()} for {self.entity}"
