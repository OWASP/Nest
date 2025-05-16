from unittest.mock import Mock, patch

import pytest

from apps.common.constants import TAB
from apps.slack.events.app_home_opened import AppHomeOpened


class TestAppHomeOpened:
    @pytest.fixture
    def mock_slack_config(self, mocker):
        mock_app = Mock()
        mocker.patch("apps.slack.apps.SlackConfig.app", mock_app)
        return mock_app

    def test_handle_event(self, mock_slack_config):
        mock_client = Mock()
        mock_event = {
            "user": "U12345",
        }

        mock_client.views_publish.return_value = {"ok": True}

        with (
            patch("apps.slack.events.app_home_opened.get_header") as mock_get_header,
        ):
            mock_get_header.return_value = [
                {"type": "section", "text": {"type": "mrkdwn", "text": "Header"}}
            ]

            handler = AppHomeOpened()
            handler.get_render_blocks = Mock(
                return_value=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Hi <@U12345>!* Welcome to the OWASP Slack Community!",
                        },
                    }
                ]
            )

            handler.handle_event(mock_event, mock_client)

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
                                "text": "*Hi <@U12345>!* Welcome to the OWASP Slack Community!",
                            },
                        },
                    ],
                },
            )

            expected_context = {
                "user_id": "U12345",
                "TAB": TAB,
            }
            handler.get_render_blocks.assert_called_once_with(expected_context)
