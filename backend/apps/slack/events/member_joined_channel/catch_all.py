"""Slack member joined any other channel handler."""

from apps.slack.apps import SlackConfig


def catch_all_handler(_event, _client, ack):
    """Slack new member cache all handler."""
    ack()


if SlackConfig.app:
    SlackConfig.app.event("member_joined_channel")(catch_all_handler)
