from unittest.mock import MagicMock, patch

import pytest
from django.test import override_settings

from apps.slack.commands.committees import Committees


@pytest.fixture(autouse=True)
def mock_get_absolute_url():
    with patch("apps.common.utils.get_absolute_url") as mock:
        mock.return_value = "https://example.com"
        yield mock


@pytest.fixture(autouse=True)
def mock_active_committees_count():
    with patch("apps.owasp.models.committee.Committee.active_committees_count") as mock:
        mock.return_value = 100
        yield mock


class TestCommitteesHandler:
    @pytest.fixture
    def mock_command(self):
        return {
            "text": "",
            "user_id": "U123456",
        }

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.fixture(autouse=True)
    def mock_get_committees(self):
        with patch("apps.owasp.index.search.committee.get_committees") as mock:
            mock.return_value = {"hits": [], "nbPages": 1}
            yield mock

    @pytest.mark.parametrize("search_query", ["", "search term"])
    @override_settings(SLACK_COMMANDS_ENABLED=True)
    def test_committees_handler(self, mock_client, mock_command, search_query):
        mock_command["text"] = search_query

        ack = MagicMock()
        Committees().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        assert mock_client.chat_postMessage.call_count == 1

    @override_settings(SLACK_COMMANDS_ENABLED=False)
    def test_committees_handler_when_commands_disabled(self, mock_client, mock_command):
        ack = MagicMock()
        Committees().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        mock_client.conversations_open.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    @override_settings(SLACK_COMMANDS_ENABLED=True)
    def test_committees_handler_with_results(self, mock_get_committees, mock_client, mock_command):
        mock_get_committees.return_value = {
            "hits": [
                {
                    "idx_name": "Test Committee",
                    "idx_summary": "Test Summary",
                    "idx_url": "https://example.com",
                    "idx_leaders": ["Leader 1"],
                }
            ],
            "nbPages": 1,
        }

        ack = MagicMock()
        Committees().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        assert any("Test Committee" in str(block) for block in blocks)
        assert any("Test Summary" in str(block) for block in blocks)
