from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.common.constants import NL
from apps.slack.commands.leaders import leaders_handler


class TestLeadersHandler:
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
    def mock_chapter(self):
        return {
            "idx_key": "test-chapter",
            "idx_leaders": ["Leader A", "Leader B"],
            "idx_name": "Test Chapter",
        }

    @pytest.fixture()
    def mock_project(self):
        return {
            "idx_key": "test-project",
            "idx_leaders": ["Leader C"],
            "idx_name": "Test Project",
        }

    @pytest.mark.parametrize(
        ("commands_enabled", "has_results", "expected_message"),
        [
            (False, True, None),
            (True, False, "No results found for"),
            (True, True, "Chapters"),
            (True, True, "Projects"),
        ],
    )
    @patch("apps.owasp.api.search.chapter.get_chapters")
    @patch("apps.owasp.api.search.project.get_projects")
    def test_handler_responses(
        self,
        mock_get_projects,
        mock_get_chapters,
        commands_enabled,
        has_results,
        expected_message,
        mock_slack_client,
        mock_slack_command,
        mock_chapter,
        mock_project,
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled

        mock_get_chapters.return_value = {"hits": [mock_chapter] if has_results else []}
        mock_get_projects.return_value = {"hits": [mock_project] if has_results else []}

        leaders_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        if not commands_enabled:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
        else:
            blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
            assert any(expected_message in str(block) for block in blocks)
            if has_results:
                assert any(mock_chapter["idx_name"] in str(block) for block in blocks)
                assert any(mock_project["idx_name"] in str(block) for block in blocks)

    @pytest.mark.parametrize(
        ("search_text", "expected_escaped"),
        [
            ("web app <>&", "web app &lt;&gt;&amp;"),
            ("normal search", "normal search"),
        ],
    )
    @patch("apps.slack.utils.escape")
    @patch("apps.owasp.api.search.chapter.get_chapters")
    @patch("apps.owasp.api.search.project.get_projects")
    def test_handler_special_characters(
        self,
        mock_get_projects,
        mock_get_chapters,
        mock_escape,
        search_text,
        expected_escaped,
        mock_slack_client,
    ):
        command = {"text": search_text, "user_id": "U123456"}

        mock_escape.return_value = expected_escaped

        settings.SLACK_COMMANDS_ENABLED = True
        mock_get_chapters.return_value = {"hits": []}
        mock_get_projects.return_value = {"hits": []}

        leaders_handler(ack=MagicMock(), command=command, client=mock_slack_client)

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]

        assert any(expected_escaped in str(block) for block in blocks)

    @pytest.mark.parametrize(
        ("leaders_list", "expected_text"),
        [
            (["Leader A", "Leader B"], f"• Leader A{NL}    • Leader B{NL}"),
            (["Leader C"], "Leader C"),
            ([], ""),
        ],
    )
    @patch("apps.owasp.api.search.chapter.get_chapters")
    @patch("apps.owasp.api.search.project.get_projects")
    def test_handler_leader_formatting(
        self,
        mock_get_projects,
        mock_get_chapters,
        leaders_list,
        expected_text,
        mock_slack_client,
        mock_slack_command,
    ):
        settings.SLACK_COMMANDS_ENABLED = True

        mock_chapter = {
            "idx_key": "test-chapter",
            "idx_leaders": leaders_list,
            "idx_name": "Test Chapter",
        }

        mock_project = {
            "idx_key": "test-project",
            "idx_leaders": ["Leader D"],
            "idx_name": "Test Project",
        }

        mock_get_chapters.return_value = {"hits": [mock_chapter]}
        mock_get_projects.return_value = {"hits": [mock_project]}

        leaders_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        block_texts = [
            block.get("text", {}).get("text", "") for block in blocks if "text" in block
        ]
        assert any(expected_text in str(block) for block in block_texts)
