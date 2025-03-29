import logging

from django.apps import AppConfig
from django.conf import settings
from slack_bolt import App

logger = logging.getLogger(__name__)


class SlackConfig(AppConfig):
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


if SlackConfig.app:

    @SlackConfig.app.error
    def error_handler(error, body, *args, **kwargs):  # noqa: ARG001
        """Handle Slack application errors.

        Args:
        ----
            error (Exception): The exception raised.
            body (dict): The payload of the Slack event that caused the error.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        logger.exception(error, extra={"body": body})

    @SlackConfig.app.use
    def log_events(client, context, logger, payload, next):  # noqa: A002, ARG001
        """Log Slack events.

        Args:
        ----
            client (slack_sdk.WebClient): The Slack WebClient instance for API calls.
            context (dict): The context of the Slack event.
            logger (logging.Logger): The logger instance.
            payload (dict): The payload of the Slack event.
            next (function): The next middleware function in the chain.

        """
        from apps.slack.models.event import Event

        try:
            Event.create(context, payload)
        except Exception:
            logger.exception("Could not log Slack event")

        next()
