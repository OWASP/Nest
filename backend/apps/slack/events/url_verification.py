"""Slack URL verification event handler."""

from apps.slack.apps import SlackConfig


def url_verification_handler(event, *_args, **_kwargs):
    """Handle Slack URL verification events.

    Args:
    ----
        event (dict): The Slack event payload.

    Returns:
    -------
        str: The challenge token to verify the URL.

    """
    return event["challenge"]


if SlackConfig.app:
    url_verification_handler = SlackConfig.app.event("url_verification")(url_verification_handler)
