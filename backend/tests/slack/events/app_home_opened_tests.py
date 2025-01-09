from unittest.mock import Mock, patch
import pytest

from apps.slack.events.app_home_opened import handler


class TestSlackHandler:
    @pytest.fixture()
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

        with patch("apps.slack.events.app_home_opened.get_header") as mock_get_header, \
                patch("apps.slack.events.app_home_opened.markdown") as mock_markdown:

            mock_get_header.return_value = [
                {"type": "section", "text": {"type": "mrkdwn", "text": "Header"}}]

            # Simulating Markdown block in the right format
            mock_markdown.return_value = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Hi <@{mock_event['user']}>!* "
                        "Welcome to the OWASP Slack Community! Here you can connect with other "
                        "members, collaborate on projects, and learn about the latest OWASP news and "
                        "events."
                    )
                }
            }

            handler(mock_event, mock_client, mock_ack)

        # Ensure that ack was called
        mock_ack.assert_called_once()

        # Check if views_publish was called correctly with expected arguments
        mock_client.views_publish.assert_called_once_with(
            user_id="U12345",
            view={
                "type": "home",
                "blocks": [
                    {"type": "section", "text": {"type": "mrkdwn", "text": "Header"}},
                    {"type": "section", "text": {
                        "type": "mrkdwn", "text": (
                            f"*Hi <@{mock_event['user']}>!* "
                            "Welcome to the OWASP Slack Community! Here you can connect with other "
                            "members, collaborate on projects, and learn about the latest OWASP news and "
                            "events."
                        )
                    }}
                ]
            }
        )
