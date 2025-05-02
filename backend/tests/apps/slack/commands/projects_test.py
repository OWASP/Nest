from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.projects import COMMAND, projects_handler


@pytest.fixture(autouse=True)
def mock_get_absolute_url():
    with patch("apps.common.utils.get_absolute_url") as mock:
        mock.return_value = "http://example.com"
        yield mock


@pytest.fixture(autouse=True)
def mock_active_projects_count():
    with patch("apps.owasp.models.project.Project.active_projects_count") as mock:
        mock.return_value = 100
        yield mock


class TestProjectsHandler:
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
    def mock_get_projects(self):
        with patch("apps.owasp.api.search.project.get_projects") as mock:
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
    def test_projects_handler(
        self, mock_client, mock_command, commands_enabled, search_query, expected_calls
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_command["text"] = search_query

        projects_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        assert mock_client.chat_postMessage.call_count == expected_calls

    def test_projects_handler_with_results(self, mock_get_projects, mock_client, mock_command):
        settings.SLACK_COMMANDS_ENABLED = True
        test_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        mock_get_projects.return_value = {
            "hits": [
                {
                    "idx_name": "Test Project",
                    "idx_summary": "Test Summary",
                    "idx_url": "http://example.com",
                    "idx_leaders": ["Leader 1"],
                    "idx_level": "Lab",
                    "idx_contributors_count": 5,
                    "idx_forks_count": 3,
                    "idx_stars_count": 10,
                    "idx_updated_at": test_date.timestamp(),
                }
            ],
            "nbPages": 1,
        }

        projects_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        assert any("Test Project" in str(block) for block in blocks)
        assert any("Test Summary" in str(block) for block in blocks)

    @pytest.fixture
    def mock_slack_command(self):
        return {
            "user_id": "U123456",
            "text": "test query",
        }

    @pytest.fixture
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C654321"}}
        return client

    @pytest.mark.parametrize(
        ("commands_enabled", "expected_call_count"),
        [
            (False, 0),
            (True, 1),
        ],
    )
    @patch("apps.slack.commands.projects.get_blocks")
    def test_handler_responses(
        self,
        mock_get_blocks,
        commands_enabled,
        expected_call_count,
        mock_slack_client,
        mock_slack_command,
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "Test blocks"}}]
        mock_get_blocks.return_value = mock_blocks

        projects_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        assert mock_get_blocks.call_count == expected_call_count

        if commands_enabled:
            mock_slack_client.conversations_open.assert_called_once_with(
                users=mock_slack_command["user_id"]
            )
            mock_slack_client.chat_postMessage.assert_called_once()

            call_args = mock_slack_client.chat_postMessage.call_args[1]
            assert call_args["blocks"] == mock_blocks
            assert call_args["channel"] == "C123456"
        else:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()

    @patch("apps.slack.commands.projects.get_blocks")
    def test_projects_handler_with_empty_query(self, mock_get_blocks, mock_slack_client):
        mock_command = {"user_id": "U123456", "text": "  "}
        settings.SLACK_COMMANDS_ENABLED = True

        mock_blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "Test blocks"}}]
        mock_get_blocks.return_value = mock_blocks

        projects_handler(ack=MagicMock(), command=mock_command, client=mock_slack_client)

        mock_get_blocks.assert_called_once()
        _, kwargs = mock_get_blocks.call_args
        assert kwargs["search_query"] == ""

    @patch("apps.slack.apps.SlackConfig.app")
    def test_command_registration(self, mock_app):
        import importlib

        from apps.slack.commands import projects

        mock_command_decorator = MagicMock()
        mock_app.command.return_value = mock_command_decorator

        importlib.reload(projects)

        mock_app.command.assert_called_once_with(COMMAND)
        assert mock_command_decorator.call_count == 1
        assert mock_command_decorator.call_args[0][0].__name__ == "projects_handler"
