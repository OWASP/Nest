"""Base class and common functionality for Slack events."""

import logging
from typing import Optional

from django.conf import settings
from slack_sdk.errors import SlackApiError
from apps.slack.template_loader import env
from apps.slack.blocks import markdown
from apps.slack.apps import SlackConfig
from apps.common.constants import NL

logger = logging.getLogger(__name__)

class EventBase:
    """Base class for Slack events with common functionality.

    Template formatting notes (if using templates):
    - Use "{{ SECTION_BREAK }}" to separate content into different Slack blocks
    - Use "{{ DIVIDER }}" to insert a horizontal divider
    """

    event_type: Optional[str] = None
    matchers = None

    @staticmethod
    def get_events():
        """Get all event handlers."""
        yield from EventBase.__subclasses__()

    @staticmethod
    def configure_events():
        """Configure all event handlers."""
        if SlackConfig.app is None:
            logger.warning("SlackConfig.app is None. Events not registered.")
            return

        for event_class in EventBase.get_events():
            event_class().register()

    def register(self):
        """Register this event handler with the Slack app."""
        if self.matchers:
            SlackConfig.app.event(self.event_type, matchers=self.matchers)(self.handler)
        else:
            SlackConfig.app.event(self.event_type)(self.handler)

    def handler(self, event, client, ack):
        """Handle the Slack event.

        Args:
            event (dict): The Slack event payload.
            client (WebClient): The Slack WebClient instance.
            ack (function): Acknowledge function.
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
            logger.exception("Slack API error handling %s", self.event_type)
            self.handle_error(event, client, e)
        except Exception as e:
            logger.exception("Error handling %s", self.event_type)
            self.handle_error(event, client, e)

    def handle_event(self, event, client):
        """Main event handling logic to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement handle_event")

    def handle_error(self, event, client, error):
        """Handle errors during event processing."""

        try:
            if "user" in event or "user_id" in event:
                user_id = event.get("user") or event.get("user_id")
                conv = self.open_conversation(client, user_id)
                if conv:
                    client.chat_postMessage(
                        channel=conv["channel"]["id"],
                        text=":warning: An error occurred processing your request."
                    )
        except Exception:
            logger.exception("Failed to send error notification")

    def open_conversation(self, client, user_id):
        """Helper to open DM conversation."""
        try:
            return client.conversations_open(users=user_id)
        except SlackApiError as e:
            if e.response["error"] == "cannot_dm_bot":
                return None
            raise

    def get_render_blocks(self, context):
        """Get rendered blocks from template (if using templates)."""
        blocks = []
        for section in self.get_render_text(context).split("{{ SECTION_BREAK }}"):
            if section.strip() == "{{ DIVIDER }}":
                blocks.append({"type": "divider"})
            elif section:
                blocks.append(markdown(section))
        return blocks

    def get_render_text(self, context):
        """Get rendered text from template (if using templates)."""
        return self.get_template_file().render(**self.get_template_context(context))

    def get_template_context(self, context):
        """Get template context (if using templates)."""
        return {
            "NL": NL,
            "DIVIDER": "{{ DIVIDER }}",
            "SECTION_BREAK": "{{ SECTION_BREAK }}",
            **context
        }

    def get_template_file(self):
        """Get template file (if using templates)."""
        template_name = self.get_template_file_name()
        try:
            return env.get_template(template_name)
        except Exception:
            logger.exception("Failed to load template '%s'", template_name)
            raise

    def get_template_file_name(self):
        """Get template file name (if using templates)."""
        return f"events/{self.__class__.__name__.lower()}.jinja"