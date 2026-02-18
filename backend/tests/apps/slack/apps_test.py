"""Tests for apps.slack.apps module."""

import importlib
import logging
import sys
from unittest.mock import MagicMock, patch

from django.test import override_settings


class TestSlackAppHandlers:
    """Tests for error_handler and log_events registered on SlackConfig.app."""

    @staticmethod
    def _reload_with_mock_app():
        """Reload apps.slack.apps with a mocked App to capture registered handlers."""
        mock_app = MagicMock()
        handlers = {}

        def capture_error(fn):
            handlers["error"] = fn
            return fn

        def capture_use(fn):
            handlers["use"] = fn
            return fn

        mock_app.error = capture_error
        mock_app.use = capture_use
        original_module = sys.modules.get("apps.slack.apps")
        with (
            override_settings(SLACK_BOT_TOKEN="xoxb-test", SLACK_SIGNING_SECRET="test-secret"),  # noqa: S106
            patch("slack_bolt.App", return_value=mock_app),
        ):
            import apps.slack.apps as module  # noqa: PLC0415

            importlib.reload(module)

        return handlers, module, original_module

    @staticmethod
    def _restore_module(original_module):
        """Restore apps.slack.apps to its original state."""
        if original_module is not None:
            sys.modules["apps.slack.apps"] = original_module
        else:
            sys.modules.pop("apps.slack.apps", None)

    def test_error_handler_logs_exception(self):
        """Test error_handler logs the error with body context."""
        handlers, module, orig = self._reload_with_mock_app()
        try:
            assert "error" in handlers
            error_handler = handlers["error"]

            test_error = Exception("Test error")
            test_body = {"event": "test"}

            with patch.object(module, "logger") as mock_logger:
                error_handler(test_error, test_body)

            mock_logger.exception.assert_called_once_with(test_error, extra={"body": test_body})
        finally:
            self._restore_module(orig)

    def test_log_events_creates_event_and_calls_next(self):
        """Test log_events creates Event and calls next()."""
        handlers, _, orig = self._reload_with_mock_app()
        try:
            assert "use" in handlers
            log_events = handlers["use"]

            mock_client = MagicMock()
            mock_context = {"team_id": "T123"}
            mock_logger = MagicMock(spec=logging.Logger)
            mock_payload = {"type": "event_callback"}
            mock_next = MagicMock()

            with patch("apps.slack.models.event.Event.create") as mock_create:
                log_events(mock_client, mock_context, mock_logger, mock_payload, mock_next)

            mock_create.assert_called_once_with(mock_context, mock_payload)
            mock_next.assert_called_once()
        finally:
            self._restore_module(orig)

    def test_log_events_handles_exception(self):
        """Test log_events catches exceptions from Event.create."""
        handlers, _, orig = self._reload_with_mock_app()
        try:
            assert "use" in handlers
            log_events = handlers["use"]

            mock_client = MagicMock()
            mock_context = {"team_id": "T123"}
            mock_logger = MagicMock(spec=logging.Logger)
            mock_payload = {"type": "event_callback"}
            mock_next = MagicMock()

            with patch("apps.slack.models.event.Event.create", side_effect=Exception("DB error")):
                log_events(mock_client, mock_context, mock_logger, mock_payload, mock_next)

            mock_logger.exception.assert_called_once_with("Could not log Slack event")
            mock_next.assert_called_once()
        finally:
            self._restore_module(orig)
