from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.projects import handler


class TestProjectsHandler:
    @pytest.fixture()
    def mock_slack_command(self):
        return {
            "text": "web application",
            "user_id": "U123456",
        }

    @pytest.fixture()
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.fixture()
    def mock_project(self):
        return {
            "idx_name": "Test Project",
            "idx_summary": "Test summary",
            "idx_url": "http://example.com/project/1",
            "idx_contributors_count": 10,
            "idx_forks_count": 5,
            "idx_stars_count": 100,
            "idx_updated_at": "2024-12-01",
            "idx_level": "Level 1",
            "idx_leaders": ["Leader A", "Leader B"],
        }

    @pytest.mark.parametrize(
        ("commands_enabled", "has_results", "expected_message"),
        [
            (False, True, None),  # Disabled commands
            (True, False, "No results found for"),  # No results
            (True, True, "Here are top 10 most OWASP projects"),  # With results
        ],
    )
    @patch("apps.owasp.api.search.project.get_projects")
    def test_handler_responses(
        self,
        mock_get_projects,
        commands_enabled,
        has_results,
        expected_message,
        mock_slack_client,
        mock_slack_command,
        mock_project,
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_get_projects.return_value = {"hits": [mock_project] if has_results else []}

        handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        if not commands_enabled:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
        else:
            blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
            assert any(expected_message in str(block) for block in blocks)
            if has_results:
                assert any(mock_project["idx_name"] in str(block) for block in blocks)
                assert any(mock_project["idx_url"] in str(block) for block in blocks)
                assert any(mock_project["idx_summary"] in str(block) for block in blocks)

    @pytest.mark.parametrize(
        ("search_text", "expected_escaped"),
        [
            ("web app <>&", "web app &lt;&gt;&amp;"),
            ("normal search", "normal search"),
        ],
    )
    @patch("apps.owasp.api.search.project.get_projects")
    def test_handler_special_characters(
        self,
        mock_get_projects,
        search_text,
        expected_escaped,
        mock_slack_client,
    ):
        command = {"text": search_text, "user_id": "U123456"}
        mock_get_projects.return_value = {"hits": []}
        settings.SLACK_COMMANDS_ENABLED = True

        handler(ack=MagicMock(), command=command, client=mock_slack_client)

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        assert any(expected_escaped in str(block) for block in blocks)

    @pytest.mark.parametrize(
        ("field", "expected_text"),
        [
            ("contributors_count", "10 contributors"),
            ("forks_count", "5 forks"),
            ("stars_count", "100 stars"),
            ("leaders", "Leader A, Leader B"),
        ],
    )
    @patch("apps.owasp.api.search.project.get_projects")
    def test_handler_field_formatting(
        self,
        mock_get_projects,
        field,
        expected_text,
        mock_slack_client,
        mock_slack_command,
        mock_project,
    ):
        mock_get_projects.return_value = {"hits": [mock_project]}
        settings.SLACK_COMMANDS_ENABLED = True

        handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        assert any(expected_text in str(block) for block in blocks)
