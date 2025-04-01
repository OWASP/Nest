from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.committees import COMMAND, committees_handler


class TestCommitteesHandler:
    @pytest.fixture(autouse=True)
    def mock_get_absolute_url(self):
        with patch("apps.common.utils.get_absolute_url") as mock:
            mock.return_value = "http://example.com"
            yield mock

    @pytest.fixture(autouse=True)
    def mock_active_committees_count(self):
        with patch("apps.owasp.models.committee.Committee.active_committees_count") as mock:
            mock.return_value = 100
            yield mock

    @pytest.fixture()
    def mock_command(self):
        return {"text": "", "user_id": "U123456"}

    @pytest.fixture()
    def mock_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.fixture(autouse=True)
    def mock_get_blocks(self):
        with patch("apps.slack.common.handlers.committees.get_blocks", autospec=True) as mock:
            mock.return_value = [
                {"type": "section", "text": {"type": "mrkdwn", "text": "Test Committee"}}
            ]
            yield mock

    @pytest.fixture(autouse=True)
    def mock_get_committees(self):
        with patch("apps.owasp.api.search.committee.get_committees") as mock:
            mock.return_value = {"hits": [], "nbPages": 1}
            yield mock

    @pytest.mark.parametrize(
        ("commands_enabled", "search_query", "expected_calls"),
        [
            (True, "", 1),
            (True, "search term", 1),
            (False, "", 0),
        ],
    )
    def test_committees_handler(
        self, mock_client, mock_command, commands_enabled, search_query, expected_calls
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_command["text"] = search_query

        committees_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        assert mock_client.chat_postMessage.call_count == expected_calls

    def test_committees_handler_with_results(self, mock_get_committees, mock_client, mock_command):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_get_committees.return_value = {
            "hits": [
                {
                    "idx_name": "Test Committee",
                    "idx_summary": "Test Summary",
                    "idx_url": "http://example.com",
                    "idx_leaders": ["Leader 1"],
                }
            ],
            "nbPages": 1,
        }

        committees_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        assert mock_client.chat_postMessage.called

    @pytest.mark.parametrize(
        "command_text",
        ["", "test search"],
    )
    def test_committees_handler_search(
        self, mock_client, mock_command, mock_get_blocks, command_text
    ):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = command_text

        with patch(
            "apps.slack.common.handlers.committees.get_blocks",
            return_value=mock_get_blocks.return_value,
        ):
            committees_handler(ack=MagicMock(), command=mock_command, client=mock_client)

            mock_client.chat_postMessage.assert_called_once()

    def test_command_registration(self):
        with patch("apps.slack.apps.SlackConfig.app") as mock_app:
            mock_command_decorator = MagicMock()
            mock_app.command.return_value = mock_command_decorator

            import importlib

            import apps.slack.commands.committees

            importlib.reload(apps.slack.commands.committees)

            mock_app.command.assert_called_once_with(COMMAND)
            assert mock_command_decorator.call_count == 1
