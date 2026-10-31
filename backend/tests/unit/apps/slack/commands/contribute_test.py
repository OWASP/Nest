from unittest.mock import MagicMock, patch

import pytest
from django.test import override_settings

from apps.slack.commands.contribute import Contribute


@pytest.fixture(autouse=True)
def mock_get_absolute_url():
    with patch("apps.common.utils.get_absolute_url") as mock:
        mock.return_value = "https://example.com"
        yield mock


class TestContributeHandler:
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
    def mock_get_contributions(self):
        with patch("apps.owasp.index.search.issue.get_issues") as mock:
            mock.return_value = {"hits": [], "nbPages": 1}
            yield mock

    @pytest.fixture(autouse=True)
    def mock_issue_active_contribute_count(self):
        with patch(
            "apps.github.models.issue.Issue.open_issues_count", new_callable=MagicMock
        ) as mock:
            mock.return_value = 10
            yield mock

    @pytest.mark.parametrize("command_text", ["", "search term", "-h"])
    @override_settings(SLACK_COMMANDS_ENABLED=True)
    def test_contribute_handler(self, mock_client, mock_command, command_text):
        mock_command["text"] = command_text

        ack = MagicMock()
        Contribute().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        assert mock_client.chat_postMessage.call_count == 1

    @override_settings(SLACK_COMMANDS_ENABLED=False)
    def test_contribute_handler_when_commands_disabled(self, mock_client, mock_command):
        ack = MagicMock()
        Contribute().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        mock_client.conversations_open.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    @override_settings(SLACK_COMMANDS_ENABLED=True)
    def test_contribute_handler_with_results(
        self, mock_get_contributions, mock_client, mock_command
    ):
        mock_get_contributions.return_value = {
            "hits": [
                {
                    "idx_title": "Test Contribution",
                    "idx_project_name": "Test Project",
                    "idx_project_url": "https://example.com/project",
                    "idx_summary": "Test Summary",
                    "idx_url": "https://example.com/contribution",
                }
            ],
            "nbPages": 1,
        }

        ack = MagicMock()
        Contribute().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        assert any("Test Contribution" in str(block) for block in blocks)
        assert any("Test Project" in str(block) for block in blocks)
