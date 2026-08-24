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
    def external_id(self, root: EntityChannel) -> str | None:
        """Platform-specific channel ID."""
        return (
            channel.slack_channel_id
            if (channel := root.channel) and channel.slack_channel_id
            else None
        )

    @strawberry_django.field
    def name(self, root: EntityChannel) -> str | None:
        """Channel display name."""
        return channel.name if (channel := root.channel) and channel.name else None
