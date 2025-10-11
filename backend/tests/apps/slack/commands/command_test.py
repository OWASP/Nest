from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from apps.slack.blocks import DIVIDER, SECTION_BREAK
from apps.slack.commands.command import CommandBase


class Command(CommandBase):
    pass


class TestCommandBase:
    @pytest.fixture
    def command_instance(self):
        return Command()

    @pytest.fixture
    def mock_command_payload(self):
        return {"user_id": "U123ABC"}

    @patch("apps.slack.commands.command.logger")
    @patch("apps.slack.commands.command.SlackConfig")
    def test_configure_commands_when_app_is_none(self, mock_slack_config, mock_logger):
        """Tests that a warning is logged if the Slack app is not configured."""
        mock_slack_config.app = None
        CommandBase.configure_commands()
        mock_logger.warning.assert_called_once()

    def test_command_name_property(self, command_instance):
        """Tests that the command_name is derived correctly from the class name."""
        assert command_instance.command_name == "/command"

    def test_template_path_property(self, command_instance):
        """Tests that the template_path is derived correctly."""
        assert command_instance.template_path == Path("commands/command.jinja")

    @patch("apps.slack.commands.command.env")
    def test_template_property(self, mock_jinja_env, command_instance):
        """Tests that the correct template is requested from the jinja environment."""
        _ = command_instance.template

        mock_jinja_env.get_template.assert_called_once_with("commands/command.jinja")

    def test_render_blocks(self, command_instance):
        """Tests that the render_blocks method correctly parses rendered text into blocks."""
        test_string = f"Hello World{SECTION_BREAK}{DIVIDER}{SECTION_BREAK}Welcome to Nest"

        with patch.object(command_instance, "render_text", return_value=test_string):
            blocks = command_instance.render_blocks(command={})

        assert len(blocks) == 3
        assert blocks[0]["text"]["text"] == "Hello World"
        assert blocks[1]["type"] == "divider"
        assert blocks[2]["text"]["text"] == "Welcome to Nest"

    def test_handler_success(self, settings, command_instance, mock_command_payload):
        """Tests the successful path of the command handler."""
        settings.SLACK_COMMANDS_ENABLED = True
        ack = MagicMock()
        mock_client = MagicMock()
        mock_client.conversations_open.return_value = {"channel": {"id": "D123XYZ"}}

        with patch.object(command_instance, "render_blocks", return_value=[{"type": "section"}]):
            command_instance.handler(ack=ack, command=mock_command_payload, client=mock_client)

        ack.assert_called_once()
        mock_client.conversations_open.assert_called_once_with(users="U123ABC")
        mock_client.chat_postMessage.assert_called_once()
        assert mock_client.chat_postMessage.call_args[1]["channel"] == "D123XYZ"

    def test_handler_api_error(self, mocker, settings, command_instance, mock_command_payload):
        """Tests that an exception during API calls is caught and logged."""
        settings.SLACK_COMMANDS_ENABLED = True
        mock_logger = mocker.patch("apps.slack.commands.command.logger")
        ack = MagicMock()
        mock_client = MagicMock()
        mock_client.chat_postMessage.side_effect = [Exception("API Error"), {"ok": True}]
        mocker.patch.object(command_instance, "render_blocks", return_value=[{"type": "section"}])
        command_instance.handler(ack=ack, command=mock_command_payload, client=mock_client)
        ack.assert_called_once()
        mock_logger.exception.assert_called_once()
        # Verify retry occurred and eventually succeeded
        assert mock_client.chat_postMessage.call_count == 2
        mock_logger.exception.assert_called_with(
            "Failed to handle command '%s'", command_instance.command_name
        )

    def test_handler_when_commands_disabled(
        self, settings, command_instance, mock_command_payload
    ):
        """Tests that no message is sent when commands are disabled."""
        settings.SLACK_COMMANDS_ENABLED = False
        ack = MagicMock()
        mock_client = MagicMock()
        command_instance.handler(ack=ack, command=mock_command_payload, client=mock_client)
        ack.assert_called_once()
        mock_client.chat_postMessage.assert_not_called()
