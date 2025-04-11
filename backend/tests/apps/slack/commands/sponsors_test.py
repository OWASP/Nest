"""Test sponsors command handler."""

from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.common.constants import OWASP_WEBSITE_URL
from apps.slack.commands.sponsors import COMMAND, sponsors_handler


class MockSponsor:
    def __init__(self, name, member_type, description, url):
        self.name = name
        self.member_type = member_type
        self.description = description
        self.url = url


mock_sponsors = [
    MockSponsor(
        name="Example Sponsor 1",
        member_type="Platinum",
        description="A top-tier sponsor.",
        url="https://example.com/sponsor1",
    ),
    MockSponsor(
        name="Example Sponsor 2",
        member_type="Gold",
        description="A mid-tier sponsor.",
        url="https://example.com/sponsor2",
    ),
]


class TestSponsorsHandler:
    """Test sponsors command handler."""

    @pytest.fixture
    def mock_slack_command(self):
        return {
            "user_id": "U123456",
        }

    @pytest.fixture
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.fixture
    def mock_sponsors(self):
        class MockSponsor:
            def __init__(self, name, url, member_type, description):
                self.name = name
                self.url = url
                self.member_type = member_type
                self.description = description

        return [
            MockSponsor(
                "Sponsor 1", "https://example.com/sponsor1", "Diamond", "Description for sponsor 1"
            ),
            MockSponsor("Sponsor 2", None, "Gold", "Description for sponsor 2"),
        ]

    @pytest.mark.parametrize(
        ("commands_enabled", "has_sponsors", "expected_message"),
        [
            (False, True, None),
            (True, True, "*OWASP Sponsors:*"),
            (True, False, "Failed to get OWASP sponsor data."),
        ],
    )
    @patch("apps.slack.commands.sponsors.get_sponsors_data")
    def test_handler_responses(
        self,
        mock_get_sponsors_data,
        commands_enabled,
        has_sponsors,
        expected_message,
        mock_slack_client,
        mock_slack_command,
        mock_sponsors,
    ):
        """Test handler responses."""
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_get_sponsors_data.return_value = mock_sponsors if has_sponsors else []

        sponsors_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        if not commands_enabled:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
        elif has_sponsors:
            mock_slack_client.conversations_open.assert_called_once_with(
                users=mock_slack_command["user_id"]
            )
            blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
            assert blocks[0]["text"]["text"] == expected_message

            assert "*1. <https://example.com/sponsor1|Sponsor 1>*" in blocks[1]["text"]["text"]
            assert "Member Type: Diamond" in blocks[1]["text"]["text"]

            assert "*2. Sponsor 2*" in blocks[2]["text"]["text"]
            assert "Member Type: Gold" in blocks[2]["text"]["text"]

            assert OWASP_WEBSITE_URL in blocks[4]["text"]["text"]
        else:
            mock_slack_client.chat_postMessage.assert_called_once_with(
                channel=mock_slack_command["user_id"],
                text="Failed to get OWASP sponsor data.",
            )

    @patch("apps.slack.apps.SlackConfig.app")
    def test_command_registration(self, mock_app):
        import importlib

        from apps.slack.commands import sponsors

        mock_command_decorator = MagicMock()
        mock_app.command.return_value = mock_command_decorator

        importlib.reload(sponsors)

        mock_app.command.assert_called_once_with(COMMAND)
        assert mock_command_decorator.call_count == 1
        assert mock_command_decorator.call_args[0][0].__name__ == "sponsors_handler"
