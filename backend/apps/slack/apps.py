"""Slack app config."""

import logging

from django.apps import AppConfig
from django.conf import settings
from slack_bolt import App
from slack_sdk import WebClient

logger: logging.Logger = logging.getLogger(__name__)


class SlackConfig(AppConfig):
    """Slack app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.slack"

    app = (
        App(
            signing_secret=settings.SLACK_SIGNING_SECRET,
            token=settings.SLACK_BOT_TOKEN,
        )
        if settings.SLACK_BOT_TOKEN != "None" and settings.SLACK_SIGNING_SECRET != "None"  # noqa: S105
        else None
    )

    def ready(self):
        """Configure Slack events when the app is ready."""
        super().ready()
        from apps.slack.events import configure_slack_events  # noqa: PLC0415

        configure_slack_events()


if SlackConfig.app:

    @SlackConfig.app.error
    def error_handler(error, body, *args, **kwargs) -> None:  # noqa: ARG001
        """Handle Slack application errors.

        Args:
            error (Exception): The exception raised.
            body (dict): The payload of the Slack event that caused the error.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        logger.exception(error, extra={"body": body})

    @SlackConfig.app.use
    def log_events(
        client: WebClient,  # noqa: ARG001
        context: dict,
        logger: logging.Logger,
        payload: dict,
        next,  # noqa: A002
    ) -> None:
        """Log Slack events.

        Args:
            client (slack_sdk.WebClient): The Slack WebClient instance for API calls.
            context (dict): The context of the Slack event.
            logger (logging.Logger): The logger instance.
            payload (dict): The payload of the Slack event.
            next (function): The next middleware function in the chain.

        """
        from apps.slack.models.event import Event  # noqa: PLC0415

        try:
            Event.create(context, payload)
        except Exception:
            logger.exception("Could not log Slack event")

        next()
