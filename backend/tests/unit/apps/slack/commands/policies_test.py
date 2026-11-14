from unittest.mock import MagicMock

import pytest
from django.test import override_settings

from apps.common.constants import NL
from apps.slack.commands.policies import Policies

EXPECTED_BLOCK_COUNT = 4


class TestPoliciesHandler:
    @pytest.fixture
    def mock_command(self):
        return {"user_id": "U123456"}

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @override_settings(SLACK_COMMANDS_ENABLED=True)
    def test_policies_handler(self, mock_client, mock_command):
        ack = MagicMock()
        Policies().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        assert mock_client.chat_postMessage.call_count == 1

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        assert len(blocks) == EXPECTED_BLOCK_COUNT
        policies_list = [
            ("Chapters Policy", "https://owasp.org/www-policy/operational/chapters"),
            (
                "Code of Conduct",
                "https://owasp.org/www-policy/operational/code-of-conduct",
            ),
            ("Committees Policy", "https://owasp.org/www-policy/operational/committees"),
            (
                "Conflict Resolution Policy",
                "https://owasp.org/www-policy/operational/conflict-resolution",
            ),
            ("Copyright Policy", "https://owasp.org/www-policy/operational/copyright"),
            (
                "Conflict of Interest Policy",
                "https://owasp.org/www-policy/operational/conflict-of-interest",
            ),
            ("Donations Policy", "https://owasp.org/www-policy/operational/donations"),
            ("Elections Policy", "https://owasp.org/www-policy/operational/election"),
            ("Events Policy", "https://owasp.org/www-policy/operational/events"),
            (
                "Expense Policy",
                "https://owasp.org/www-policy/operational/expense-reimbursement",
            ),
            ("Grant Policy", "https://owasp.org/www-policy/operational/grants"),
            ("Membership Policy", "https://owasp.org/www-policy/operational/membership"),
            ("Project Policy", "https://owasp.org/www-policy/operational/projects"),
            ("Privacy Policy", "https://owasp.org/www-policy/operational/privacy"),
            (
                "Whistleblower Policy",
                "https://owasp.org/www-policy/operational/whistleblower",
            ),
        ]
        expected_policies = NL.join(f"  • <{url}|{title}>" for title, url in policies_list)
        expected_block0 = f"Important OWASP policies:{NL}{expected_policies}"
        assert blocks[0]["text"]["text"].strip() == expected_block0.strip()
        assert blocks[1]["type"] == "divider"
        expected_footer = (
            "Please visit <https://owasp.org/www-policy/|OWASP policies> page for more information"
        )
        assert blocks[2]["text"]["text"].strip() == expected_footer
        assert blocks[3]["type"] == "section"
        assert blocks[3]["text"]["type"] == "mrkdwn"
        assert "💬 You can share feedback" in blocks[3]["text"]["text"]

    @override_settings(SLACK_COMMANDS_ENABLED=False)
    def test_policies_handler_when_commands_disabled(self, mock_client, mock_command):
        ack = MagicMock()
        Policies().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        mock_client.conversations_open.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()
