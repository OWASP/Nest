"""Test sponsors command handler."""

from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.sponsors import sponsors_handler


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

    @pytest.fixture()
    def mock_slack_command(self):
        return {
            "user_id": "U123456",
        }

    @pytest.fixture()
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.mark.parametrize(
        ("commands_enabled", "has_sponsors_data", "expected_header"),
        [
            (False, True, None),
            (True, True, "*OWASP Sponsors:*"),
            (True, False, "*OWASP Sponsors:*"),
        ],
    )
    @patch("apps.slack.commands.sponsors.get_sponsors_data")
    def test_handler_responses(
        self,
        mock_get_sponsors_data,
        commands_enabled,
        has_sponsors_data,
        expected_header,
        mock_slack_client,
        mock_slack_command,
    ):
        """Test handler responses."""
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_get_sponsors_data.return_value = mock_sponsors if has_sponsors_data else []

        sponsors_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        if not commands_enabled:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
            return

        if not has_sponsors_data:
            mock_slack_client.chat_postMessage.assert_called_once_with(
                channel=mock_slack_command["user_id"],
                text="Failed to get OWASP sponsor data.",
            )
            mock_slack_client.conversations_open.assert_not_called()
            return

        mock_slack_client.conversations_open.assert_called_once_with(
            users=mock_slack_command["user_id"]
        )

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]

        assert blocks[0]["text"]["text"] == expected_header

        if has_sponsors_data:
            current_block = 1

            sponsor_block = blocks[current_block]["text"]["text"]
            assert "*1. <https://example.com/sponsor1|Example Sponsor 1>*" in sponsor_block
            assert "Member Type: Platinum" in sponsor_block
            assert "A top-tier sponsor." in sponsor_block
            current_block += 1

            sponsor_block = blocks[current_block]["text"]["text"]
            assert "*2. <https://example.com/sponsor2|Example Sponsor 2>*" in sponsor_block
            assert "Member Type: Gold" in sponsor_block
            assert "A mid-tier sponsor." in sponsor_block
            current_block += 1

            assert blocks[current_block]["type"] == "divider"
            current_block += 1

            footer_block = blocks[current_block]["text"]["text"]
            assert (
                "* Please visit the <https://owasp.org/supporters|OWASP supporters>"
                in footer_block
            )
            assert "for more information about the sponsors" in footer_block
