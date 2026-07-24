"""Slack reaction services."""

import logging

from django.db import IntegrityError
from slack_sdk.errors import SlackApiError

from apps.slack.blocks import markdown
from apps.slack.models import Conversation
from apps.slack.models.reaction_alert import ReactionAlert
from apps.slack.models.reaction_rule import ReactionRule

logger = logging.getLogger(__name__)


def process_reaction_added(event, client):
    """Process Slack reaction_added events for moderation alerts."""
    details = get_message_reaction_details(event)
    if details is None:
        return

    channel_id, message_ts, emoji_name = details
    conversation, rule = get_reaction_rule(channel_id, emoji_name)
    if rule is None:
        return

    reaction_count = get_reaction_count(client, channel_id, message_ts, emoji_name)
    if reaction_count < rule.threshold:
        return

    reaction_alert, created = get_or_create_alert(
        conversation,
        message_ts,
        rule.report_type,
        reaction_count,
    )
    if not created:
        return

    permalink = get_permalink(client, channel_id, message_ts)
    if not permalink:
        reaction_alert.delete()
        return

    text = build_alert_text(rule, channel_id, emoji_name, reaction_count, permalink)
    alert = post_alert(client, rule.alert_channel_id, text)
    if alert is None:
        reaction_alert.delete()
        return

    update_alert_message_ts(reaction_alert, alert)


def get_message_reaction_details(event):
    """Extract message reaction details from a Slack event."""
    item = event.get("item", {})
    if item.get("type") != "message":
        return None

    channel_id = item.get("channel")
    message_ts = item.get("ts")
    emoji_name = event.get("reaction")

    if not channel_id or not message_ts or not emoji_name:
        return None

    return channel_id, message_ts, emoji_name


def get_reaction_rule(channel_id, emoji_name):
    """Get the matching conversation and reaction rule, if configured."""
    try:
        conversation = Conversation.objects.get(slack_channel_id=channel_id)
        rule = ReactionRule.objects.get(
            conversation=conversation,
            emoji_name=emoji_name,
            is_enabled=True,
        )
    except (Conversation.DoesNotExist, ReactionRule.DoesNotExist):
        return None, None

    return conversation, rule


def get_reaction_count(client, channel_id, message_ts, emoji_name):
    """Get the current unique user count for a reaction."""
    try:
        response = client.reactions_get(channel=channel_id, timestamp=message_ts)
    except SlackApiError as e:
        logger.warning(
            "Could not fetch Slack reactions for moderation: %s",
            e.response.get("error", "unknown_error"),
        )
        return 0

    message = response.get("message", {})
    for reaction in message.get("reactions", []):
        if reaction.get("name") == emoji_name:
            return reaction.get("count", len(set(reaction.get("users", []))))

    return 0


def get_or_create_alert(conversation, message_ts, report_type, reaction_count):
    """Atomically claim the moderation alert before posting to Slack."""
    for _attempt in range(2):
        try:
            return ReactionAlert.objects.get_or_create(
                conversation=conversation,
                message_ts=message_ts,
                report_type=report_type,
                defaults={"reaction_count": reaction_count},
            )
        except IntegrityError:
            try:
                return (
                    ReactionAlert.objects.get(
                        conversation=conversation,
                        message_ts=message_ts,
                        report_type=report_type,
                    ),
                    False,
                )
            except ReactionAlert.DoesNotExist:
                continue

    return None, False


def get_permalink(client, channel_id, message_ts):
    """Get the Slack permalink for the reported message."""
    try:
        return client.chat_getPermalink(
            channel=channel_id,
            message_ts=message_ts,
        )["permalink"]
    except SlackApiError as e:
        logger.warning(
            "Could not fetch Slack permalink for moderation alert: %s",
            e.response.get("error", "unknown_error"),
        )
        return ""


def post_alert(client, channel_id, text):
    """Post a moderation alert to Slack."""
    try:
        return client.chat_postMessage(
            channel=channel_id,
            blocks=[markdown(text)],
            text=text,
        )
    except SlackApiError as e:
        logger.warning(
            "Could not post Slack moderation alert: %s",
            e.response.get("error", "unknown_error"),
        )
        return None


def update_alert_message_ts(reaction_alert, alert):
    """Record the Slack notification timestamp on the claimed alert."""
    reaction_alert.alert_message_ts = alert.get("ts", "")
    reaction_alert.save(update_fields=["alert_message_ts"])


def build_alert_text(rule, channel_id, emoji_name, reaction_count, permalink):
    """Build the Slack moderation alert message."""
    mentions = " ".join(f"<@{user_id}>" for user_id in rule.alert_user_ids or [])

    return (
        f"{mentions}\n"
        f":{emoji_name}: {rule.report_type} report threshold reached in <#{channel_id}>.\n"
        f"Count: {reaction_count}\n"
        f"{permalink}"
    ).strip()
