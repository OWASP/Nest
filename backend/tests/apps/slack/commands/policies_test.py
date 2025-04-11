from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.common.constants import NL
from apps.slack.commands.policies import COMMAND, policies_handler

EXPECTED_BLOCK_COUNT = 3


class TestPoliciesHandler:
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
        "commands_enabled",
        [False, True],
    )
    def test_handler_responses(
        self,
        commands_enabled,
        mock_slack_client,
        mock_slack_command,
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled

        policies_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        if not commands_enabled:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
        else:
            mock_slack_client.conversations_open.assert_called_once_with(
                users=mock_slack_command["user_id"]
            )
            mock_slack_client.chat_postMessage.assert_called_once()

            blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]

            assert len(blocks) == EXPECTED_BLOCK_COUNT
            assert "Important OWASP policies:" in blocks[0]["text"]["text"]
            assert "Chapters Policy" in blocks[0]["text"]["text"]
            assert "Project Policy" in blocks[0]["text"]["text"]
            assert blocks[1]["type"] == "divider"
            assert "OWASP policies" in blocks[2]["text"]["text"]

    @patch("apps.slack.apps.SlackConfig.app")
    def test_command_registration(self, mock_app):
        import importlib

        from apps.slack.commands import policies

        mock_command_decorator = MagicMock()
        mock_app.command.return_value = mock_command_decorator

        importlib.reload(policies)

        mock_app.command.assert_called_once_with(COMMAND)
        assert mock_command_decorator.call_count == 1
        assert mock_command_decorator.call_args[0][0].__name__ == "policies_handler"

    @pytest.mark.parametrize(("commands_enabled", "expected_calls"), [(True, 1), (False, 0)])
    def test_policies_handler(
        self, mock_slack_client, mock_slack_command, commands_enabled, expected_calls
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        ack = MagicMock()
        policies_handler(ack=ack, command=mock_slack_command, client=mock_slack_client)
        ack.assert_called_once()
        assert mock_slack_client.chat_postMessage.call_count == expected_calls
        if commands_enabled:
            mock_slack_client.conversations_open.assert_called_once_with(
                users=mock_slack_command["user_id"]
            )
            blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
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
