"""OWASP app entity channel GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.models.entity_channel import EntityChannel


@strawberry_django.type(
    EntityChannel,
    fields=[
        "is_active",
        "is_default",
        "is_reviewed",
        "platform",
    ],
)
class EntityChannelNode(strawberry.relay.Node):
    """Entity channel node."""

    @strawberry_django.field
    def name(self, root: EntityChannel) -> str:
        """Channel display name from the linked Slack Conversation."""
        conv = root.channel
        return conv.name if conv else ""

    @strawberry_django.field
    def slack_channel_id(self, root: EntityChannel) -> str:
        """Slack channel ID for linking (e.g. C123ABC)."""
        conv = root.channel
        return conv.slack_channel_id if conv else ""
