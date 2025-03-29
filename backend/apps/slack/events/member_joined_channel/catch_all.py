"""Slack member joined any other channel handler."""

from apps.slack.apps import SlackConfig
from apps.slack.constants import OWASP_CONTRIBUTE_CHANNEL_ID, OWASP_GSOC_CHANNEL_ID


def catch_all_handler(event, client, ack):  # noqa: ARG001
    """Slack new member cache all handler.

    Args:
    ----
        event (dict): The event payload from Slack.
        client (slack_sdk.WebClient): The Slack WebClient instance.
        ack (Callable): The acknowledgment function to confirm event processing.

    """
    ack()


if SlackConfig.app:
    SlackConfig.app.event(
        "member_joined_channel",
        matchers=[
            lambda event: f"#{event['channel']}"
            not in {
                OWASP_CONTRIBUTE_CHANNEL_ID,
                OWASP_GSOC_CHANNEL_ID,
            }
        ],
    )(catch_all_handler)
