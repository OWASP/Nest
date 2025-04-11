from unittest.mock import Mock, patch

import pytest
from slack_sdk.errors import SlackApiError

from apps.slack.events.app_home_opened import app_home_opened_handler


class TestSlackHandler:
    @pytest.fixture
    def mock_slack_config(self, mocker):
        mock_app = Mock()
        mocker.patch("apps.slack.apps.SlackConfig.app", mock_app)
        return mock_app

    def test_handler_app_home_opened(self, mock_slack_config):
        mock_ack = Mock()
        mock_client = Mock()
        mock_event = {
            "user": "U12345",
        }

        mock_client.views_publish.return_value = {"ok": True}

        with (
            patch("apps.slack.events.app_home_opened.get_header") as mock_get_header,
            patch("apps.slack.events.app_home_opened.markdown") as mock_markdown,
        ):
            mock_get_header.return_value = [
                {"type": "section", "text": {"type": "mrkdwn", "text": "Header"}}
            ]

            mock_markdown.return_value = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Hi <@{mock_event['user']}>!* Welcome to the OWASP Slack Community!"
                    ),
                },
            }

            app_home_opened_handler(mock_event, mock_client, mock_ack)

            mock_ack.assert_called_once()

            mock_client.views_publish.assert_called_once_with(
                user_id="U12345",
                view={
                    "type": "home",
                    "blocks": [
                        {"type": "section", "text": {"type": "mrkdwn", "text": "Header"}},
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": (
                                    f"*Hi <@{mock_event['user']}>!* "
                                    "Welcome to the OWASP Slack Community!"
                                ),
                            },
                        },
                    ],
                },
            )

    @patch("apps.slack.events.app_home_opened.settings.SLACK_EVENTS_ENABLED", new=False)
    def test_handler_events_disabled(self):
        mock_ack = Mock()
        mock_client = Mock()
        mock_event = {"user": "U12345"}

        app_home_opened_handler(mock_event, mock_client, mock_ack)

        mock_ack.assert_called_once()
        mock_client.views_publish.assert_not_called()

    def test_handler_slack_api_error(self):
        mock_ack = Mock()
        mock_client = Mock()
        mock_event = {"user": "U12345"}

        error_response = {"error": "operation_failed"}
        mock_client.views_publish.side_effect = SlackApiError(
            "Failed to publish view", error_response
        )

        with (
            patch("apps.slack.events.app_home_opened.get_header"),
            patch("apps.slack.events.app_home_opened.markdown"),
            patch("apps.slack.events.app_home_opened.logger") as mock_logger,
        ):
            app_home_opened_handler(mock_event, mock_client, mock_ack)

            mock_ack.assert_called_once()
            mock_client.views_publish.assert_called_once()
            mock_logger.exception.assert_called_once()

    @patch("apps.slack.apps.SlackConfig.app")
    def test_event_registration(self, mock_app):
        import importlib

        from apps.slack.events import app_home_opened

        importlib.reload(app_home_opened)

        mock_app.event.assert_called_once_with("app_home_opened")
