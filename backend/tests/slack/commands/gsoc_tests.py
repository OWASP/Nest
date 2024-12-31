from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.blocks import markdown
from apps.slack.commands.gsoc import handler


class TestGsocHandler:
    @pytest.fixture()
    def mock_slack_command(self):
        return {
            "text": "",
            "user_id": "U123456",
        }

    @pytest.fixture()
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.mark.parametrize(
        ("commands_enabled", "command_text", "expected_message"),
        [
            (False, "", None),  # Disabled commands case
            (True, "", "GSOC_GENERAL_INFORMATION_BLOCKS"),  # Empty text case
            (True, "invalid", "Usage: `/gsoc [year]`"),  # Invalid text case
            (True, "2024", "No projects found for GSOC 2024"),  # Valid year, no projects case
        ],
    )
    def test_handler_responses(
        self, commands_enabled, command_text, expected_message, mock_slack_client
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        command = {"text": command_text, "user_id": "U123456"}

        with patch(
            "apps.slack.common.gsoc.GSOC_GENERAL_INFORMATION_BLOCKS",
            new=[markdown("GSOC_GENERAL_INFORMATION_BLOCKS")],
        ), patch(
            "apps.slack.commands.gsoc.get_gsoc_projects_by_year",
            return_value={"hits": []},
        ):
            handler(ack=MagicMock(), command=command, client=mock_slack_client)

            if not commands_enabled:
                mock_slack_client.conversations_open.assert_not_called()
                mock_slack_client.chat_postMessage.assert_not_called()
            else:
                blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
                block_texts = [str(block) for block in blocks]
                assert any(expected_message in block_text for block_text in block_texts)

    def test_handler_with_projects(self, mock_slack_client):
        """Test handler when projects are found for a valid year."""
        mock_projects = {
            "hits": [
                {
                    "idx_name": "Test Project",
                    "idx_summary": "Project summary",
                    "idx_type": "Documentation",
                    "idx_level": "Beginner",
                    "idx_url": "https://owasp.org/www-project-bug-logging-tool/",
                }
            ]
        }

        command = {"text": "2024", "user_id": "U123456"}
        settings.SLACK_COMMANDS_ENABLED = True

        with patch(
            "apps.slack.commands.gsoc.get_gsoc_projects_by_year",
            return_value=mock_projects,
        ):
            handler(ack=MagicMock(), command=command, client=mock_slack_client)

            blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
            project_block = str(blocks[0])

            assert "Test Project" in project_block
            assert "Project summary" in project_block
            assert "Type: Documentation" in project_block
            assert "Level: Beginner" in project_block
            assert "https://owasp.org/www-project-bug-logging-tool/" in project_block
