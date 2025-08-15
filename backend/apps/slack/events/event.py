"""Base class and common functionality for Slack events."""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from django.conf import settings
from jinja2 import Template
from slack_sdk.errors import SlackApiError

from apps.common.constants import NL, TAB
from apps.common.utils import convert_to_snake_case
from apps.slack.apps import SlackConfig
from apps.slack.blocks import DIVIDER, SECTION_BREAK, markdown
from apps.slack.constants import FEEDBACK_SHARING_INVITE, NEST_BOT_NAME
from apps.slack.template_loader import env
from apps.slack.utils import get_text

logger = logging.getLogger(__name__)


class EventBase:
    """Base class for Slack events."""

    event_type: str | None = None
    matchers: list[Callable[[Any], bool]] | None = None

    @staticmethod
    def configure_events():
        """Configure all event handlers with the Slack app."""
        if SlackConfig.app is None:
            logger.warning("SlackConfig.app is None. Event handlers are not registered.")
            return

        for event in EventBase.get_events():
            event().register()

    @staticmethod
    def get_events():
        """Yield all subclasses of EventBase."""
        yield from EventBase.__subclasses__()

    @property
    def direct_message_template(self) -> Template | None:
        """Get the Jinja template file for direct message.

        Returns:
            Template | None: The Jinja template object or None.

        """
        return (
            env.get_template(str(self.direct_message_template_path))
            if self.direct_message_template_path
            else None
        )

    @property
    def direct_message_template_path(self) -> Path | None:
        """Get the Jinja template file path for direct message.

        Returns:
            Path | None: The Jinja template path or None.

        """
        return Path(f"events/{convert_to_snake_case(self.__class__.__name__)}.jinja")

    @property
    def ephemeral_message_template(self) -> Template | None:
        """Get the Jinja template file for ephemeral message.

        Returns:
            Template | None: The Jinja template object or None.

        """
        return (
            env.get_template(str(self.ephemeral_message_template_path))
            if self.ephemeral_message_template_path
            else None
        )

    @property
    def ephemeral_message_template_path(self) -> Path | None:
        """Get the Jinja template file path for ephemeral message.

        Ephemeral messages are optional so it returns None by default
        but can be overridden in subclasses.

        Returns:
            Path | None: The Jinja template path or None.

        """
        return None

    def get_context(self, event: dict) -> dict:
        """Build the template context, including base variables and the provided context.

        Args:
            event (dict): The event- or handler-specific context.

        Returns:
            dict: The complete context for template rendering.

        """
        return {
            "DIVIDER": DIVIDER,
            "FEEDBACK_SHARING_INVITE": FEEDBACK_SHARING_INVITE,
            "NEST_BOT_NAME": NEST_BOT_NAME,
            "NL": NL,
            "SECTION_BREAK": SECTION_BREAK,
            "OWASP_NEST_NAME": "OWASP Nest",
            "OWASP_NEST_URL": settings.SITE_URL,
            "TAB": TAB,
            "USER_ID": self.get_user_id(event),
        }

    def get_direct_message(self, event) -> list[dict]:
        """Get the direct message blocks.

        Args:
            event (dict): The Slack event payload.

        """
        return self.render_blocks(self.direct_message_template, self.get_context(event))

    def get_ephemeral_message(self, event) -> list[dict]:
        """Get the ephemeral message blocks.

        Args:
            event (dict): The Slack event payload.

        """
        return self.render_blocks(self.ephemeral_message_template, self.get_context(event))

    def get_user_id(self, event) -> str:
        """Get the user ID from the event.

        Args:
            event (dict): The Slack event payload.

        Returns:
            str: The user ID.

        """
        return event.get("user", event.get("user_id"))

    def handler(self, event, client, ack):
        """Handle the Slack event.

        Args:
            event (dict): The Slack event payload.
            client (WebClient): The Slack WebClient instance.
            ack (Callable): Function to acknowledge the event.

        """
        ack()

        if not settings.SLACK_EVENTS_ENABLED:
            return

        try:
            self.handle_event(event, client)
        except SlackApiError as e:
            if e.response["error"] == "cannot_dm_bot":
                logger.warning("Cannot DM bot user in event %s", self.event_type)
                return
            raise
        except Exception:
            logger.exception("Error handling %s", self.event_type)

    def handle_event(self, event, client):
        """Implement event handling logic.

        Args:
            event (dict): The Slack event payload.
            client (WebClient): The Slack WebClient instance.

        """
        user_id = self.get_user_id(event)

        # Send direct message.
        if (
            direct_message := self.render_blocks(
                self.direct_message_template,
                self.get_context(event),
            )
        ) and (conversation := self.open_conversation(client, user_id)):
            client.chat_postMessage(
                blocks=direct_message,
                channel=conversation["channel"]["id"],
                text=get_text(direct_message),
            )

        # Send ephemeral message.
        if ephemeral_message := self.render_blocks(
            self.ephemeral_message_template,
            self.get_context(event),
        ):
            client.chat_postEphemeral(
                blocks=ephemeral_message,
                channel=event["channel"],
                text=get_text(ephemeral_message),
                user=user_id,
            )

    def open_conversation(self, client, user_id):
        """Open a DM conversation with a user.

        Args:
            client (WebClient): The Slack WebClient instance.
            user_id (str): The Slack user ID.

        Returns:
            dict or None: The conversation object, or None if cannot DM bot.

        """
        if not user_id:
            return None

        try:
            return client.conversations_open(users=user_id)
        except SlackApiError as e:
            if e.response["error"] == "cannot_dm_bot":
                return None
            raise

    def render_blocks(self, template, context):
        """Render Slack blocks from the template using the provided context.

        Args:
            template (Template): The template for rendering.
            context (dict): The context for template rendering.

        Returns:
            list: List of Slack block objects.

        """
        if not template:
            return []

        blocks = []
        for section in self.render_text(template, context).split(SECTION_BREAK):
            if section.strip() == DIVIDER:
                blocks.append({"type": "divider"})
            elif section:
                blocks.append(markdown(section))

        return blocks

    def render_text(self, template: Template, context: dict) -> str:
        """Render template as plain text using the provided context.

        Args:
            template (Template): The template for rendering.
            context (dict): The context for template rendering.

        Returns:
            str: The rendered text.

        """
        return template.render(context)

    def register(self):
        """Register this event handler with the Slack app."""
        SlackConfig.app.event(self.event_type, matchers=self.matchers)(self.handler)
