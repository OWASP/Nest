"""Slack bot URL verification event handler."""

from apps.slack.apps import SlackConfig


def url_verification_handler(event, *_args, **_kwargs):
    """Slack URL verification handler."""
    return event["challenge"]


if SlackConfig.app:
    SlackConfig.app.event("url_verification")(url_verification_handler)
