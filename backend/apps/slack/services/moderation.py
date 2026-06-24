"""Slack moderation services."""

import logging

from django.db import IntegrityError
from slack_sdk.errors import SlackApiError

from apps.slack.blocks import markdown
from apps.slack.models import Conversation
from apps.slack.models.moderation import ModerationAlert, ModerationRule

logger = logging.getLogger(__name__)


def process_reaction_added(event, client):
    """Process Slack reaction_added events for moderation alerts."""
    details = _get_message_reaction_details(event)
    if details is None:
        return

    channel_id, message_ts, emoji_name = details
    conversation, rule = _get_moderation_rule(channel_id, emoji_name)
    if rule is None:
        return

    reaction_count = _get_reaction_count(client, channel_id, message_ts, emoji_name)
    if reaction_count < rule.threshold:
        return

    moderation_alert, created = _get_or_create_alert(
        conversation,
        message_ts,
        rule.report_type,
        reaction_count,
    )
    if not created:
        return

    permalink = _get_permalink(client, channel_id, message_ts)
    if not permalink:
        moderation_alert.delete()
        return

    text = _build_alert_text(rule, channel_id, emoji_name, reaction_count, permalink)
    alert = _post_alert(client, rule.alert_channel_id, text)
    if alert is None:
        moderation_alert.delete()
        return

    _update_alert_message_ts(moderation_alert, alert)


def _get_message_reaction_details(event):
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


def _get_moderation_rule(channel_id, emoji_name):
    """Get the matching conversation and moderation rule, if configured."""
    try:
        conversation = Conversation.objects.get(slack_channel_id=channel_id)
        rule = ModerationRule.objects.get(
            conversation=conversation,
            emoji_name=emoji_name,
            is_enabled=True,
        )
    except (Conversation.DoesNotExist, ModerationRule.DoesNotExist):
        return None, None

    return conversation, rule


def _get_reaction_count(client, channel_id, message_ts, emoji_name):
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


def _get_or_create_alert(conversation, message_ts, report_type, reaction_count):
    """Atomically claim the moderation alert before posting to Slack."""
    for _attempt in range(2):
        try:
            return ModerationAlert.objects.get_or_create(
                conversation=conversation,
                message_ts=message_ts,
                report_type=report_type,
                defaults={"reaction_count": reaction_count},
            )
        except IntegrityError:
            try:
                return (
                    ModerationAlert.objects.get(
                        conversation=conversation,
                        message_ts=message_ts,
                        report_type=report_type,
                    ),
                    False,
                )
            except ModerationAlert.DoesNotExist:
                continue

    return None, False


def _get_permalink(client, channel_id, message_ts):
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


def _post_alert(client, channel_id, text):
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


def _update_alert_message_ts(moderation_alert, alert):
    """Record the Slack notification timestamp on the claimed alert."""
    moderation_alert.alert_message_ts = alert.get("ts", "")
    moderation_alert.save(update_fields=["alert_message_ts"])


def _build_alert_text(rule, channel_id, emoji_name, reaction_count, permalink):
    """Build the Slack moderation alert message."""
    mentions = " ".join(f"<@{user_id}>" for user_id in rule.alert_user_ids or [])

    return (
        f"{mentions}\n"
        f":{emoji_name}: {rule.report_type} report threshold reached in <#{channel_id}>.\n"
        f"Count: {reaction_count}\n"
        f"{permalink}"
    ).strip()
