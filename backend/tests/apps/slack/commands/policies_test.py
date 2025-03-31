from unittest.mock import MagicMock

import pytest
from django.conf import settings

from apps.common.constants import NL
from apps.slack.commands.policies import policies_handler

EXPECTED_BLOCK_COUNT = 3


class TestPoliciesHandler:
    @pytest.fixture
    def mock_command(self):
        return {"user_id": "U123456"}

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.mark.parametrize(("commands_enabled", "expected_calls"), [(True, 1), (False, 0)])
    def test_policies_handler(self, mock_client, mock_command, commands_enabled, expected_calls):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        ack = MagicMock()
        policies_handler(ack=ack, command=mock_command, client=mock_client)
        ack.assert_called_once()
        assert mock_client.chat_postMessage.call_count == expected_calls
        if commands_enabled:
            mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
            blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
            assert len(blocks) == EXPECTED_BLOCK_COUNT
            expected_policies = NL.join(
                f"  • <{url}|{title}>"
                for title, url in [
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
                    (
                        "Whistleblower & Anti-Retaliation Policy",
                        "https://owasp.org/www-policy/operational/whistleblower",
                    ),
                ]
            )
            expected_block0 = f"Important OWASP policies:{NL}{expected_policies}"
            assert blocks[0]["text"]["text"] == expected_block0
            assert blocks[1]["type"] == "divider"
            expected_footer = (
                "Please visit <https://owasp.org/www-policy/|OWASP policies> page for more "
                "information"
                f"{NL}"
            )
            assert blocks[2]["text"]["text"] == expected_footer
