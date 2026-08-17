"""Handle Slack reaction_added events."""

import logging

from slack_sdk.errors import SlackApiError

from apps.slack.blocks import markdown
from apps.slack.events.event import EventBase
from apps.slack.models.reaction_alert import ReactionAlert
from apps.slack.models.reaction_rule import ReactionRule
from apps.slack.utils.reaction import (
    format_emojis,
    mention_users,
    parse_message_reaction,
    reaction_from_payload,
)

logger = logging.getLogger(__name__)


def fetch_permalink(client, channel_id: str, message_ts: str) -> str:
    """Return a Slack permalink for the message, or an empty string."""
    try:
        return (
            client.chat_getPermalink(
                channel=channel_id,
                message_ts=message_ts,
            ).get("permalink")
            or ""
        )
    except SlackApiError as e:
        logger.warning(
            "Could not fetch Slack permalink for moderation alert: %s",
            e.response.get("error", "unknown_error"),
        )
        return ""


def fetch_reaction(client, channel_id: str, message_ts: str, emojis: list[str]):
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

    return reaction_from_payload(payload, emojis)


class ReactionAdded(EventBase):
    """Handle reaction_added events for moderation alerts."""

    event_type = "reaction_added"

    def handle_event(self, event, client):
        """Post an alert when Slack shows the rule threshold is reached."""
        if (details := parse_message_reaction(event)) is None:
            return

        channel_id, message_ts, emoji_name = details
        if (rule := ReactionRule.for_emoji(channel_id, emoji_name)) is None:
            return

        if ReactionAlert.exists_for(rule.conversation, message_ts, rule.report_type):
            return

        if (snapshot := fetch_reaction(client, channel_id, message_ts, rule.emojis)) is None:
            return

        reaction_count, reporter_user_ids, permalink = snapshot
        if reaction_count < rule.threshold:
            return

        # Lock in-flight posts; the DB row is written only after Slack succeeds.
        if (
            owner := ReactionAlert.acquire(rule.conversation, message_ts, rule.report_type)
        ) is None:
            return

        try:
            if not permalink:
                permalink = fetch_permalink(client, channel_id, message_ts)

            if ReactionAlert.renew(rule.conversation, message_ts, rule.report_type, owner):
                alert_users = mention_users(rule.alert_user_ids)
                reporters = mention_users(reporter_user_ids)
                emojis = format_emojis(rule.emojis)
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

                try:
                    alert = client.chat_postMessage(
                        blocks=[markdown(text)],
                        channel=rule.alert_channel_id,
                        text=text,
                    )
                except SlackApiError as e:
                    logger.warning(
                        "Could not post Slack moderation alert: %s",
                        e.response.get("error", "unknown_error"),
                    )
                else:
                    ReactionAlert.record(
                        rule.conversation,
                        message_ts,
                        rule.report_type,
                        reaction_count,
                        alert.get("ts", ""),
                        reporter_user_ids=reporter_user_ids,
                    )
        finally:
            ReactionAlert.release(rule.conversation, message_ts, rule.report_type, owner)
