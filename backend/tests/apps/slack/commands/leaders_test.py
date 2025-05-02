from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.leaders import COMMAND, leaders_handler


class TestLeadersHandler:
    TEST_CHAPTER = "Test Chapter"
    TEST_PROJECT = "Test Project"
    CHAPTER_LEADER_1 = "Chapter Leader 1"
    CHAPTER_LEADER_2 = "Test Chapter Leader 2"
    PROJECT_LEADER_1 = "Project Leader 1"
    PROJECT_LEADER_2 = "Test Project Leader 2"

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

    @pytest.fixture
    def mock_get_chapters(self):
        with patch("apps.owasp.api.search.chapter.get_chapters") as mock:
            mock.return_value = {"hits": []}
            yield mock

    @pytest.fixture
    def mock_get_projects(self):
        with patch("apps.owasp.api.search.project.get_projects") as mock:
            mock.return_value = {"hits": []}
            yield mock

    @pytest.fixture(autouse=True)
    def mock_get_absolute_url(self):
        with patch("apps.slack.commands.leaders.get_absolute_url") as mock:
            mock.return_value = "http://example.com/test"
            yield mock

    def test_handler_disabled(self, mock_command, mock_client):
        settings.SLACK_COMMANDS_ENABLED = False

        leaders_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    def test_handler_no_results(
        self, mock_command, mock_client, mock_get_chapters, mock_get_projects
    ):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = "nonexistent"

        leaders_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert "No results found for" in text
        assert "nonexistent" in text

        mock_get_chapters.assert_called_once()
        mock_get_projects.assert_called_once()

    def test_handler_with_chapter_results(
        self, mock_command, mock_client, mock_get_chapters, mock_get_projects
    ):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = "test"

        mock_get_chapters.return_value = {
            "hits": [
                {
                    "idx_key": "test-chapter",
                    "idx_name": self.TEST_CHAPTER,
                    "idx_leaders": ["Leader 1", "Test Leader 2"],
                }
            ]
        }

        leaders_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert "Chapters" in text
        assert self.TEST_CHAPTER in text
        assert "Leader 1" in text
        assert "`Test Leader 2`" in text

    def test_handler_with_project_results(
        self, mock_command, mock_client, mock_get_chapters, mock_get_projects
    ):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = "test"

        mock_get_projects.return_value = {
            "hits": [
                {
                    "idx_key": "test-project",
                    "idx_name": self.TEST_PROJECT,
                    "idx_leaders": [self.PROJECT_LEADER_1, self.PROJECT_LEADER_2],
                }
            ]
        }

        leaders_handler(ack=MagicMock(), command=mock_command, client=mock_client)
        leaders_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert "Projects" in text
        assert self.TEST_PROJECT in text
        assert self.PROJECT_LEADER_1 in text
        assert f"`{self.PROJECT_LEADER_2}`" in text

    def test_handler_with_both_results(
        self, mock_command, mock_client, mock_get_chapters, mock_get_projects
    ):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = "test"

        mock_get_chapters.return_value = {
            "hits": [
                {
                    "idx_key": "test-chapter",
                    "idx_name": self.TEST_CHAPTER,
                    "idx_leaders": [self.CHAPTER_LEADER_1, self.CHAPTER_LEADER_2],
                }
            ]
        }

        mock_get_projects.return_value = {
            "hits": [
                {
                    "idx_key": "test-project",
                    "idx_name": self.TEST_PROJECT,
                    "idx_leaders": [self.PROJECT_LEADER_1, self.PROJECT_LEADER_2],
                }
            ]
        }

        leaders_handler(ack=MagicMock(), command=mock_command, client=mock_client)
        leaders_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert "Chapters" in text
        assert self.TEST_CHAPTER in text
        assert self.CHAPTER_LEADER_1 in text
        assert f"`{self.CHAPTER_LEADER_2}`" in text

        assert "Projects" in text
        assert self.TEST_PROJECT in text
        assert self.PROJECT_LEADER_1 in text
        assert f"`{self.PROJECT_LEADER_2}`" in text

    def test_handler_with_no_leaders(
        self, mock_command, mock_client, mock_get_chapters, mock_get_projects
    ):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = "test"

        mock_get_chapters.return_value = {
            "hits": [
                {
                    "idx_key": "test-chapter",
                    "idx_name": self.TEST_CHAPTER,
                    "idx_leaders": [],
                }
            ]
        }

        mock_get_projects.return_value = {
            "hits": [
                {
                    "idx_key": "test-project",
                    "idx_name": self.TEST_PROJECT,
                    "idx_leaders": None,
                }
            ]
        }

        leaders_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.chat_postMessage.assert_called_once()
        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]

        assert len(blocks) > 0

        headers_text = "".join(str(block) for block in blocks)
        assert "Chapters" in headers_text
        assert "Projects" in headers_text

        assert self.TEST_CHAPTER not in headers_text
        assert self.TEST_PROJECT not in headers_text

    def test_handler_with_empty_query(
        self, mock_command, mock_client, mock_get_chapters, mock_get_projects
    ):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = ""

        leaders_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_get_chapters.assert_called_once()
        mock_get_projects.assert_called_once()

    @patch("apps.slack.apps.SlackConfig.app")
    def test_command_registration(self, mock_app):
        import importlib

        from apps.slack.commands import leaders

        mock_command_decorator = MagicMock()
        mock_app.command.return_value = mock_command_decorator

        importlib.reload(leaders)

        mock_app.command.assert_called_once_with(COMMAND)
        assert mock_command_decorator.call_count == 1
        assert mock_command_decorator.call_args[0][0].__name__ == "leaders_handler"
