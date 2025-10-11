from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

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

    @pytest.mark.parametrize(
        ("commands_enabled", "command_text", "expected_calls"),
        [
            (True, "", 1),
            (True, "search term", 1),
            (True, "-h", 1),
            (False, "", 0),
        ],
    )
    def test_contribute_handler(
        self, mock_client, mock_command, commands_enabled, command_text, expected_calls
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_command["text"] = command_text

        ack = MagicMock()
        Contribute().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        assert mock_client.chat_postMessage.call_count == expected_calls

    def test_contribute_handler_with_results(
        self, mock_get_contributions, mock_client, mock_command
    ):
        settings.SLACK_COMMANDS_ENABLED = True
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
