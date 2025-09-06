"""OWASP app entity member model."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.github.models.user import User


class EntityMember(models.Model):
    """EntityMember model."""

    class Role(models.TextChoices):
        CANDIDATE = "candidate", "Candidate"
        LEADER = "leader", "Leader"
        MEMBER = "member", "Member"

    class Meta:
        db_table = "owasp_entity_members"
        unique_together = (
            "entity_type",
            "entity_id",
            "member",
            "role",
        )
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["member"]),
        ]
        verbose_name_plural = "Entity members"

    description = models.CharField(
        blank=True,
        default="",
        help_text="Optional note or role description",
        max_length=100,
    )
    entity = GenericForeignKey("entity_type", "entity_id")
    entity_id = models.PositiveBigIntegerField()
    entity_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    is_active = models.BooleanField(
        default=False,
        help_text="Indicates if the membership is active",
    )
    is_reviewed = models.BooleanField(
        default=False,
        help_text="Indicates if the membership is reviewed",
    )
    member = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    member_email = models.EmailField(blank=True, default="")
    member_name = models.CharField(default="", max_length=255)
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Display order/priority of members",
    )
    role = models.CharField(
        max_length=9,
        choices=Role.choices,
        default=Role.LEADER,
    )

    def __str__(self):
        """EntityMember human readable representation."""
        display_name = self.member.login if self.member else self.member_name
        return f"{display_name} as {self.get_role_display()} for {self.entity}"
