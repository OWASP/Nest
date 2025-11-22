"""OWASP app entity channel GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.models.entity_channel import EntityChannel
from apps.slack.models.conversation import Conversation

@strawberry_django.type(
    EntityChannel,
    fields=[
        "id",
        "platform",
        "is_active",
        "is_default",
        "is_reviewed",
        "channel_id"
    ],
)
class EntityChannelNode:
    """GraphQL node for EntityChannel (links OWASP entity → Slack channel)."""
    
    @strawberry.field
    def slack_channel_id(self) -> str | None:
        """Returns the slack channel ID"""
        channel = self.channel
        if isinstance(channel , Conversation):
            return channel.slack_channel_id
        return None
    
    @strawberry.field
    def slack_channel_name(self) -> str | None:
        """Returns the slack channel name"""
        channel = self.channel 
        if isinstance(channel , Conversation):
            return channel.name
        return None
    
    @strawberry.field 
    def slack_url(self) -> str | None:
        """Returns the slack channel URL"""
        channel = self.channel 
        if isinstance(channel , Conversation) and channel.slack_channel_id:
            return  f"https://slack.com/app_redirect?channel={channel.slack_channel_id}"
        return None