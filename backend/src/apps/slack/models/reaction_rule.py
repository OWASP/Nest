"""Store channel-specific Slack reaction rules."""

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimestampedModel
from apps.slack.enums import ReportType
from apps.slack.models.conversation import Conversation


class ReactionRule(TimestampedModel):
    """Channel-specific emoji threshold and alert target."""

    class Meta:
        """Model options."""

        constraints = [
            models.UniqueConstraint(
                fields=("conversation", "report_type"),
                name="unique_reactionrule_conversation_report_type",
                violation_error_message=(
                    "A reaction rule already exists for this conversation and report type."
                ),
            ),
        ]
        db_table = "slack_reaction_rules"

    alert_channel_id = models.CharField(
        max_length=50,
        help_text="Slack channel ID where reaction alerts are posted.",
    )
    alert_user_ids = models.JSONField(
        blank=True,
        default=list,
        help_text="Slack user IDs mentioned when this reaction rule triggers.",
    )
    emojis = models.JSONField(
        blank=True,
        default=list,
        help_text="Slack emojis that trigger this reaction rule.",
    )
    is_active = models.BooleanField(default=True)
    report_type = models.CharField(
        max_length=64,
        choices=ReportType.choices,
        default=ReportType.SPAM,
        help_text="Report category recorded when this reaction rule triggers.",
    )
    threshold = models.PositiveSmallIntegerField(default=10, validators=[MinValueValidator(1)])

    # FKs.
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)

    def __str__(self):
        """Human readable representation."""
        return f"{self.conversation} {ReactionRule.format_emojis(self.emojis)}".strip()

    def clean(self):
        """Validate emojis and reject overlap with other active rules on the channel."""
        super().clean()
        names = self.emojis
        if not isinstance(names, list) or not names:
            raise ValidationError({"emojis": "Enter at least one Slack emoji."})

        cleaned = []
        seen: set[str] = set()
        for raw_name in names:
            if not isinstance(raw_name, str) or not raw_name.strip():
                raise ValidationError({"emojis": "Emojis must be non-empty strings."})
            name = raw_name.strip()
            if name.startswith(":") or name.endswith(":"):
                raise ValidationError(
                    {"emojis": "Enter emojis without colons (spam, not :spam:)."}
                )
            if name in seen:
                raise ValidationError({"emojis": f"Duplicate emoji: {name}."})
            seen.add(name)
            cleaned.append(name)
        self.emojis = cleaned

        if not self.conversation_id:
            return

        others = ReactionRule.objects.filter(
            conversation_id=self.conversation_id,
            is_active=True,
        )
        if self.pk:
            others = others.exclude(pk=self.pk)
        overlap = seen.intersection(
            name for other in others if isinstance(other.emojis, list) for name in other.emojis
        )
        if overlap:
            raise ValidationError(
                {
                    "emojis": (
                        "These emojis are already used by another rule on this "
                        f"channel: {', '.join(sorted(overlap))}."
                    )
                }
            )

    @staticmethod
    def for_emoji(channel_id: str, emoji_name: str) -> "ReactionRule | None":
        """Get the active reaction rule for a channel and emoji, if configured."""
        for rule in ReactionRule.objects.select_related("conversation").filter(
            conversation__slack_channel_id=channel_id,
            is_active=True,
        ):
            if isinstance(rule.emojis, list) and emoji_name in rule.emojis:
                return rule
        return None

    @staticmethod
    def format_emojis(emojis: object) -> str:
        """Return Slack emoji markup for the given emoji names."""
        if not emojis or not isinstance(emojis, list):
            return ""
        return " ".join(f":{name}:" for name in emojis if name)

    @staticmethod
    def parse_reactions_get(
        payload,
        emojis: object,
    ) -> tuple[int, list[str], str, list[str]] | None:
        """Return unique reporters, permalink, and matched emoji names from reactions.get."""
        if not isinstance(emojis, list):
            return None
        wanted = {name for name in emojis if name}
        if not wanted:
            return None

        message = payload.get("message") or {}
        permalink = message.get("permalink") or ""
        reporters: list[str] = []
        seen: set[str] = set()
        matched_names: set[str] = set()
        for reaction in message.get("reactions") or []:
            name = reaction.get("name")
            if name not in wanted:
                continue
            matched_names.add(name)
            for user_id in reaction.get("users") or []:
                if user_id and user_id not in seen:
                    seen.add(user_id)
                    reporters.append(user_id)
        if not matched_names:
            return None
        matched_emojis = [name for name in emojis if name in matched_names]
        return len(reporters), reporters, permalink, matched_emojis
