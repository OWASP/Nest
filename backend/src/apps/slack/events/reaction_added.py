"""Handle Slack reaction_added events."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, NamedTuple

from slack_sdk.errors import SlackApiError

from apps.slack.enums import ReportSource, ReportType
from apps.slack.events.event import EventBase
from apps.slack.models.content_report import ContentReport
from apps.slack.models.message import Message
from apps.slack.models.reaction_rule import ReactionRule
from apps.slack.utils.reaction import mention_users, parse_message_reaction

if TYPE_CHECKING:
    from slack_sdk import WebClient

logger = logging.getLogger(__name__)


class ThresholdAlertContext(NamedTuple):
    """Context for posting a reaction-threshold content-report alert."""

    channel_id: str
    matched_emojis: list[str]
    message_ts: str
    owner: str
    permalink: str
    reaction_count: int
    reporter_user_ids: list[str]
    rule: ReactionRule


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

    return ReactionRule.match_reactions(payload, emojis)


def threshold_alert_context(event, client: WebClient) -> ThresholdAlertContext | None:
    """Return alert context when a reaction rule threshold is met, else None."""
    if (details := parse_message_reaction(event)) is None:
        return None

    channel_id, message_ts, emoji_name = details
    rule = ReactionRule.for_emoji(channel_id, emoji_name)
    if (
        rule is None
        or rule.conversation.is_private
        or ContentReport.exists_for(rule.conversation, message_ts)
    ):
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

    return ThresholdAlertContext(
        channel_id=channel_id,
        matched_emojis=matched_emojis,
        message_ts=message_ts,
        owner=owner,
        permalink=permalink,
        reaction_count=reaction_count,
        reporter_user_ids=reporter_user_ids,
        rule=rule,
    )


class ReactionAdded(EventBase):
    """Handle reaction_added events for moderation alerts."""

    event_type = "reaction_added"

    def handle_event(self, event, client):
        """Post an alert when Slack shows the rule threshold is reached."""
        context = threshold_alert_context(event, client)
        if context is None:
            return

        channel_id = context.channel_id
        message_ts = context.message_ts
        rule = context.rule
        permalink = context.permalink
        owner = context.owner

        try:
            if not permalink:
                permalink = Message.fetch_permalink(client, channel_id, message_ts)

            if not ContentReport.renew(rule.conversation, message_ts, owner):
                return

            alert_users = mention_users(rule.alert_user_ids)
            reporters = mention_users(context.reporter_user_ids)
            emojis = ReactionRule.format_emojis(context.matched_emojis)
            category = (
                ReportType(rule.report_type).label
                if rule.report_type in ReportType.values
                else rule.report_type
            )
            text = (
                f"{alert_users}\n"
                f"A message in <#{channel_id}> reached the "
                f"{category.lower()} report threshold."
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
            ContentReport.post_alert(
                client,
                channel_id=rule.alert_channel_id,
                conversation=rule.conversation,
                message_ts=message_ts,
                message=message,
                reaction_count=context.reaction_count,
                report_type=rule.report_type,
                reporter_user_ids=context.reporter_user_ids,
                source=str(ReportSource.EMOJI),
                text=text,
            )
        finally:
            ContentReport.release(rule.conversation, message_ts, owner)
