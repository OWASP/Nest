"""Base class and common functionality for Slack shortcuts."""

from __future__ import annotations

import logging
from typing import Any

from apps.slack.apps import SlackConfig

logger = logging.getLogger(__name__)


class ShortcutBase:
    """Base class for Slack message shortcuts."""

    callback_id: str
    view_callback_id: str | None = None

    @staticmethod
    def configure_shortcuts() -> None:
        """Configure shortcut handlers."""
        if SlackConfig.app is None:
            logger.warning("SlackConfig.app is None. Shortcut handlers are not registered.")
            return

        for shortcut in ShortcutBase.get_shortcuts():
            shortcut().register()

    @staticmethod
    def get_shortcuts():
        """Get all shortcuts."""
        yield from ShortcutBase.__subclasses__()

    def handle(self, ack, shortcut: dict[str, Any], client, respond) -> None:
        """Handle the Slack shortcut invocation."""
        raise NotImplementedError

    def handle_view(self, ack, body: dict[str, Any], client) -> None:
        """Handle a modal view submission owned by this shortcut."""
        raise NotImplementedError

    def register(self) -> None:
        """Register this shortcut (and optional view) with the Slack app."""
        if (app := SlackConfig.app) is None:
            return

        app.shortcut(self.callback_id)(self.handle)
        if self.view_callback_id:
            app.view(self.view_callback_id)(self.handle_view)
