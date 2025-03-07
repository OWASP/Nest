from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.projects import projects_handler


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
    @pytest.fixture()
    def mock_command(self):
        return {
            "text": "",
            "user_id": "U123456",
        }

    @pytest.fixture()
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
