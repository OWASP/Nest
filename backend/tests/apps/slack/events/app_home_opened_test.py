from unittest.mock import Mock, patch

import pytest
from django.conf import settings

from apps.common.constants import TAB
from apps.slack.blocks import DIVIDER, SECTION_BREAK
from apps.slack.constants import (
    FEEDBACK_SHARING_INVITE,
    NEST_BOT_NAME,
    NL,
)
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
            handler.render_blocks = Mock(
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
                "DIVIDER": DIVIDER,
                "FEEDBACK_SHARING_INVITE": FEEDBACK_SHARING_INVITE,
                "NEST_BOT_NAME": NEST_BOT_NAME,
                "NL": NL,
                "SECTION_BREAK": SECTION_BREAK,
                "OWASP_NEST_NAME": "OWASP Nest",
                "OWASP_NEST_URL": settings.SITE_URL,
                "TAB": TAB,
                "USER_ID": "U12345",
            }
            handler.render_blocks.assert_called_once_with(
                handler.direct_message_template, expected_context
            )
