"""Handle Slack reaction_added events."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from slack_sdk.errors import SlackApiError

from apps.slack.enums import ReportSource
from apps.slack.events.event import EventBase
from apps.slack.models.content_report import ContentReport
from apps.slack.models.message import Message
from apps.slack.models.reaction_rule import ReactionRule
from apps.slack.utils.reaction import mention_users, parse_message_reaction

if TYPE_CHECKING:
    from slack_sdk import WebClient

logger = logging.getLogger(__name__)


def fetch_reaction(client: WebClient, channel_id: str, message_ts: str, emojis: list[str]):
    """Return Slack's current unique-reporter snapshot for the rule emojis, or None."""
    try:
        payload = client.reactions_get(
            channel=channel_id,
            full=True,
            timestamp=message_ts,
        )
    except SlackApiError as e:
        logger.warning(
            "Could not fetch Slack reactions for moderation alert: %s",
            e.response.get("error", "unknown_error"),
        )
        return None

    return ReactionRule.parse_reactions_get(payload, emojis)


def threshold_alert_context(event, client: WebClient):
    """Return alert context when a reaction rule threshold is met, else None."""
    if (details := parse_message_reaction(event)) is None:
        return None

    channel_id, message_ts, emoji_name = details
    rule = ReactionRule.for_emoji(channel_id, emoji_name)
    if rule is None or ContentReport.exists_for(rule.conversation, message_ts):
        return None

    snapshot = fetch_reaction(client, channel_id, message_ts, rule.emojis)
    if snapshot is None:
        return None

    reaction_count, reporter_user_ids, permalink, matched_emojis = snapshot
    if reaction_count < rule.threshold:
        return None

    owner = ContentReport.acquire(rule.conversation, message_ts)
    if owner is None:
        return None

    return (
        channel_id,
        message_ts,
        rule,
        reaction_count,
        reporter_user_ids,
        permalink,
        matched_emojis,
        owner,
    )


class ReactionAdded(EventBase):
    """Handle reaction_added events for moderation alerts."""

    event_type = "reaction_added"

    def handle_event(self, event, client):
        """Post an alert when Slack shows the rule threshold is reached."""
        context = threshold_alert_context(event, client)
        if context is None:
            return

        (
            channel_id,
            message_ts,
            rule,
            reaction_count,
            reporter_user_ids,
            permalink,
            matched_emojis,
            owner,
        ) = context

        try:
            if not permalink:
                permalink = Message.fetch_permalink(client, channel_id, message_ts)

            if not ContentReport.renew(rule.conversation, message_ts, owner):
                return

            alert_users = mention_users(rule.alert_user_ids)
            reporters = mention_users(reporter_user_ids)
            emojis = ReactionRule.format_emojis(matched_emojis)
            text = (
                f"{alert_users}\n"
                f"A message in <#{channel_id}> reached the "
                f"{rule.report_type} report threshold."
            )
            if reporters:
                text = f"{text}\nReported by: {reporters} using the following emojis: {emojis}"
            if permalink:
                text = f"{text}\n{permalink}"
            text = text.strip()

            message = Message.objects.filter(
                conversation=rule.conversation,
                slack_message_id=message_ts,
            ).first()
            ContentReport.deliver_alert(
                client,
                channel_id=rule.alert_channel_id,
                text=text,
                conversation=rule.conversation,
                message_ts=message_ts,
                report_type=rule.report_type,
                source=str(ReportSource.EMOJI),
                reporter_user_ids=reporter_user_ids,
                reaction_count=reaction_count,
                message=message,
            )
        finally:
            ContentReport.release(rule.conversation, message_ts, owner)
