from unittest.mock import ANY, MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.sponsors import SPONSOR_TIER_ORDER, Sponsors


class MockSponsor:
    def __init__(self, name, member_type, description, url):
        self.name = name
        self.member_type = member_type
        self.description = description
        self.url = url


mock_sponsors = [
    MockSponsor(
        name=f"Example Sponsor {index}",
        member_type="Platinum" if index == 1 else "Gold",
        description=f"Sponsor description {index}.",
        url=f"https://example.com/sponsor{index}",
    )
    for index in range(1, 13)
]


class TestSponsorsHandler:
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

    @pytest.mark.parametrize(
        ("commands_enabled", "has_sponsors_data", "expected_header"),
        [
            (False, True, None),
            (True, True, "*OWASP Sponsors:*"),
            (True, False, "*OWASP Sponsors:*"),
        ],
    )
    @patch("apps.slack.commands.sponsors.Sponsor.objects")
    def test_handler_responses(
        self,
        mock_sponsor_objects,
        commands_enabled,
        has_sponsors_data,
        expected_header,
        mock_slack_client,
        mock_slack_command,
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_sponsor_objects.order_by.return_value = mock_sponsors if has_sponsors_data else []

        ack = MagicMock()
        Sponsors().handler(ack=ack, command=mock_slack_command, client=mock_slack_client)

        ack.assert_called_once()

        if not commands_enabled:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
            return

        mock_sponsor_objects.order_by.assert_called_once_with(SPONSOR_TIER_ORDER, "sort_name")

        if not has_sponsors_data:
            mock_slack_client.conversations_open.assert_called_once_with(
                users=mock_slack_command["user_id"]
            )
            mock_slack_client.chat_postMessage.assert_called_once_with(
                blocks=ANY,
                channel="C123456",
                text="Failed to get OWASP sponsor data.",
            )
            return

        mock_slack_client.conversations_open.assert_called_once_with(
            users=mock_slack_command["user_id"]
        )

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]

        assert expected_header in blocks[0]["text"]["text"]

        if has_sponsors_data:
            sponsor_blocks = [
                block
                for block in blocks
                if block.get("type") == "section"
                and "Member Type:" in block.get("text", {}).get("text", "")
            ]
            assert len(sponsor_blocks) == 10
            assert (
                "*1. <https://example.com/sponsor1|Example Sponsor 1>*"
                in sponsor_blocks[0]["text"]["text"]
            )
            assert (
                "*10. <https://example.com/sponsor10|Example Sponsor 10>*"
                in sponsor_blocks[-1]["text"]["text"]
            )
            assert not any("Sponsor 11" in block["text"]["text"] for block in sponsor_blocks)

            footer_block = next(
                block["text"]["text"]
                for block in blocks
                if "OWASP Supporters" in block.get("text", {}).get("text", "")
            )
            assert (
                "* Please visit the <https://owasp.org/supporters/|OWASP Supporters>"
                in footer_block
            )
            assert "for more information about the sponsors" in footer_block

            feedback_block = next(
                block["text"]["text"]
                for block in blocks
                if "💬 You can share feedback" in block.get("text", {}).get("text", "")
            )
            assert "💬 You can share feedback" in feedback_block
