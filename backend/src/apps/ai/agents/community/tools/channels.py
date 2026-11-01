"""Tool for querying Slack channels related to OWASP entities."""

import logging

from crewai.tools import tool
from django.contrib.contenttypes.models import ContentType

from apps.owasp.models.chapter import Chapter
from apps.owasp.models.entity_channel import EntityChannel
from apps.owasp.models.project import Project
from apps.slack.models.conversation import Conversation

logger = logging.getLogger(__name__)

MAX_PURPOSE_LENGTH = 150


def format_entity_channels(entity, channels) -> str:
    """Format channels for a single entity.

    Args:
        entity: The entity (Project or Chapter)
        channels: QuerySet of EntityChannel instances

    Returns:
        Formatted string with entity name and channels

    """
    entity_name = entity.name or entity.key
    entity_type = entity.__class__.__name__.lower()

    if not channels.exists():
        return (
            f"💬 *{entity_name}* ({entity_type.title()})\n\n"
            "No Slack channels are currently linked to this entity."
        )

    formatted = f"💬 *{entity_name}* ({entity_type.title()}) - Slack Channels:\n\n"

    # Sort channels: default first, then by name
    sorted_channels = sorted(
        channels, key=lambda c: (not c.is_default, c.channel.name if c.channel else "")
    )

    for entity_channel in sorted_channels:
        try:
            channel = entity_channel.channel
            if not channel:
                continue
        except (AttributeError, ValueError) as e:
            logger.debug(
                "Channel might have been deleted but EntityChannel still references it",
                extra={"entity_channel_id": entity_channel.id, "error": str(e)},
            )
            continue

        channel_name = channel.name or "Unknown"
        channel_id = channel.slack_channel_id

        # Format channel link for Slack (Slack will render this as a clickable channel link)
        # Format: <#channel_id|channel_name> - Slack automatically adds # prefix in UI
        channel_link = f"<#{channel_id}|{channel_name}>"

        # Add default indicator with better formatting
        if entity_channel.is_default:
            formatted += f"• {channel_link} *← default channel*\n"
        else:
            formatted += f"• {channel_link}\n"

        # Add purpose if available
        if channel.purpose:
            purpose_text = channel.purpose[:MAX_PURPOSE_LENGTH]
            if len(channel.purpose) > MAX_PURPOSE_LENGTH:
                purpose_text += "..."
            formatted += f"  _{purpose_text}_\n"

        formatted += "\n"

    return formatted


@tool("Get Slack channels for an OWASP entity (project or chapter)")
def get_entity_channels(entity_name: str) -> str:
    """Get Slack channels linked to a specific OWASP entity.

    This tool returns all active Slack channels associated with a project or chapter.
    Channels are displayed with their names, links, and purposes.

    Use this tool when users ask about:
    - What Slack channels are related to [project/chapter name]?
    - Where can I find the Slack channel for [entity name]?
    - Show me channels for [project/chapter]
    - Slack channels for [entity]

    Args:
        entity_name: Name of the entity (project or chapter) to get channels for

    Returns:
        Formatted string with Slack channel information

    """
    if not entity_name or not entity_name.strip():
        return "Please provide an entity name (project or chapter) to find its Slack channels."

    entity_name = entity_name.strip()
    entity = None

    # Search in projects
    try:
        entity = Project.objects.get(name__iexact=entity_name, is_active=True)
    except Project.DoesNotExist:
        try:
            # Try by key
            key = entity_name.lower()
            if not key.startswith("www-project-"):
                key = f"www-project-{key}"
            entity = Project.objects.get(key__iexact=key, is_active=True)
        except Project.DoesNotExist:
            pass

    # Search in chapters if not found
    if not entity:
        try:
            entity = Chapter.objects.get(name__iexact=entity_name, is_active=True)
        except Chapter.DoesNotExist:
            try:
                key = entity_name.lower()
                if not key.startswith("www-chapter-"):
                    key = f"www-chapter-{key}"
                entity = Chapter.objects.get(key__iexact=key, is_active=True)
            except Chapter.DoesNotExist:
                pass

    if not entity:
        return (
            f"No active entity found with name '{entity_name}'. "
            "Please check the name and try again. "
            "This tool supports projects and chapters only."
        )

    # Get channels for this entity
    entity_type = ContentType.objects.get_for_model(entity.__class__)
    conversation_type = ContentType.objects.get_for_model(Conversation)

    channels = EntityChannel.objects.filter(
        entity_type=entity_type,
        entity_id=entity.id,
        channel_type=conversation_type,
        platform=EntityChannel.Platform.SLACK,
        is_active=True,
    )

    return format_entity_channels(entity, channels)
