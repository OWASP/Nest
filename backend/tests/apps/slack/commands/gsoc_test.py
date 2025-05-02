from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.common.constants import NL
from apps.slack.blocks import markdown
from apps.slack.commands.gsoc import (
    COMMAND,
    SUPPORTED_ANNOUNCEMENT_YEARS,
    SUPPORTED_YEARS,
    gsoc_handler,
)
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE

GSOC_START_TEXT = "Getting Started with OWASP GSoC"


class TestGsocHandler:
    @pytest.fixture
    def mock_slack_command(self):
        return {
            "text": "",
            "user_id": "U123456",
        }

    @pytest.fixture
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.fixture
    def mock_gsoc_projects(self):
        with patch("apps.slack.utils.get_gsoc_projects") as mock:
            mock.return_value = [
                {"idx_name": "Project1", "idx_url": "https://example.com/project1"},
                {"idx_name": "Project2", "idx_url": "https://example.com/project2"},
            ]
            yield mock

    @pytest.mark.parametrize(
        ("commands_enabled", "command_text", "expected_message"),
        [
            (False, "", None),
            (True, "", "GSOC_GENERAL_INFORMATION_BLOCKS"),
            (
                True,
                "invalid",
                f"*`{COMMAND} invalid` is not supported*{NL}",
            ),
            (True, "2011", "Year 2011 is not supported. Supported years: 2012-2025"),
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
        ):
            gsoc_handler(ack=MagicMock(), command=command, client=mock_slack_client)

            if not commands_enabled:
                mock_slack_client.conversations_open.assert_not_called()
                mock_slack_client.chat_postMessage.assert_not_called()
            else:
                mock_slack_client.conversations_open.assert_called_once_with(
                    users=command["user_id"]
                )
                mock_slack_client.chat_postMessage.assert_called_once()

                blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
                block_texts = [block["text"]["text"] for block in blocks]

                if command_text == "":
                    assert "GSOC_GENERAL_INFORMATION_BLOCKS" in block_texts[0]
                    assert FEEDBACK_CHANNEL_MESSAGE in block_texts[1]
                else:
                    assert any(expected_message in text for text in block_texts)

    def test_handler_with_projects(self, mock_slack_client):
        """Test handler when projects are found for a valid year."""
        mock_projects = [
            {
                "idx_name": "Test Project",
                "idx_url": "https://owasp.org/www-project-bug-logging-tool/",
            }
        ]

        command = {"text": "2024", "user_id": "U123456"}
        settings.SLACK_COMMANDS_ENABLED = True

        with patch(
            "apps.slack.utils.get_gsoc_projects",
            return_value=mock_projects,
        ):
            gsoc_handler(ack=MagicMock(), command=command, client=mock_slack_client)

            blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
            project_block = str(blocks[0])

            expected_link = "<https://owasp.org/www-project-bug-logging-tool/|Test Project>"
            assert expected_link in project_block

    def test_handler_disabled(self, mock_slack_command, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = False

        gsoc_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        mock_slack_client.conversations_open.assert_not_called()
        mock_slack_client.chat_postMessage.assert_not_called()

    def test_handler_default(self, mock_slack_command, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True

        gsoc_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        mock_slack_client.conversations_open.assert_called_once_with(
            users=mock_slack_command["user_id"]
        )
        mock_slack_client.chat_postMessage.assert_called_once()

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert GSOC_START_TEXT in text
        assert "feedback" in text.lower()

    def test_handler_start_command(self, mock_slack_command, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_slack_command["text"] = "--start"

        gsoc_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert GSOC_START_TEXT in text

    @pytest.mark.parametrize("year", [max(SUPPORTED_YEARS), min(SUPPORTED_YEARS), 2023])
    def test_handler_valid_year(
        self, mock_slack_command, mock_slack_client, mock_gsoc_projects, year
    ):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_slack_command["text"] = str(year)

        gsoc_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert f"GSoC {year} projects" in text
        assert "Project1" in text
        assert "Project2" in text
        mock_gsoc_projects.assert_called_once_with(year)

    def test_handler_announcement_year(
        self, mock_slack_command, mock_slack_client, mock_gsoc_projects
    ):
        settings.SLACK_COMMANDS_ENABLED = True
        year = max(SUPPORTED_ANNOUNCEMENT_YEARS)
        mock_slack_command["text"] = str(year)

        gsoc_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert f"GSoC {year} announcement" in text
        assert f"GSoC {year} ideas" in text

    def test_handler_unsupported_year(self, mock_slack_command, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        unsupported_year = max(SUPPORTED_YEARS) + 10
        mock_slack_command["text"] = str(unsupported_year)

        gsoc_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert f"Year {unsupported_year} is not supported" in text
        assert "Supported years" in text

    def test_handler_invalid_command(self, mock_slack_command, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_slack_command["text"] = "invalid_command"

        gsoc_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert "is not supported" in text

    @patch("apps.slack.apps.SlackConfig.app")
    def test_command_registration(self, mock_app):
        import importlib

        from apps.slack.commands import gsoc

        mock_command_decorator = MagicMock()
        mock_app.command.return_value = mock_command_decorator

        importlib.reload(gsoc)

        mock_app.command.assert_called_once_with(COMMAND)
        assert mock_command_decorator.call_count == 1
        assert mock_command_decorator.call_args[0][0].__name__ == "gsoc_handler"
