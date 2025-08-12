"""OWASP app entity member model."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.github.models import User


class EntityMember(models.Model):
    """EntityMember model."""

    class MemberKind(models.TextChoices):
        LEADER = "leader", "Leader"

    class Meta:
        db_table = "owasp_entity_members"
        unique_together = ("content_type", "object_id", "member", "kind")
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
        verbose_name_plural = "Entity Members"

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    entity = GenericForeignKey("content_type", "object_id")

    description = models.TextField(blank=True, help_text="Optional role or description")
    is_reviewed = models.BooleanField(
        default=False, help_text="Indicates if the membership is verified"
    )
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="entity_memberships")
    order = models.PositiveIntegerField(default=0, help_text="Display order/priority of members")

    kind = models.CharField(max_length=20, choices=MemberKind.choices, default=MemberKind.LEADER)

    def __str__(self):
        """EntityMember human readable representation."""
        return f"{self.member.login} as {self.get_kind_display()} for {self.entity}"
