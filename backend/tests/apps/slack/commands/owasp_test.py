from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.owasp import owasp_handler


class TestOwaspHandler:
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
    def mock_get_committees(self):
        with patch("apps.owasp.api.search.committee.get_committees") as mock:
            mock.return_value = {"hits": []}
            yield mock

    @pytest.fixture
    def mock_get_projects(self):
        with patch("apps.owasp.api.search.project.get_projects") as mock:
            mock.return_value = {"hits": []}
            yield mock

    @pytest.fixture(autouse=True)
    def mock_get_absolute_url(self):
        with patch("apps.common.utils.get_absolute_url") as mock:
            mock.return_value = "http://example.com"
            yield mock

    @pytest.fixture(autouse=True)
    def _mock_active_counts(self):
        with (
            patch("apps.owasp.models.chapter.Chapter.active_chapters_count") as mock_chapters,
            patch(
                "apps.owasp.models.committee.Committee.active_committees_count"
            ) as mock_committees,
            patch("apps.owasp.models.project.Project.active_projects_count") as mock_projects,
        ):
            mock_chapters.return_value = 100
            mock_committees.return_value = 100
            mock_projects.return_value = 100
            yield

    @pytest.mark.parametrize(
        ("commands_enabled", "command_text", "expected_help"),
        [
            (True, "", True),
            (True, "-h", True),
            (True, "invalid_command", False),
            (False, "", False),
        ],
    )
    def test_owasp_handler(
        self, mock_client, mock_command, commands_enabled, command_text, expected_help
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_command["text"] = command_text

        owasp_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        if commands_enabled:
            blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
            if expected_help:
                assert any("chapters" in str(block) for block in blocks)
                assert any("committees" in str(block) for block in blocks)
                assert any("projects" in str(block) for block in blocks)
            elif "invalid_command" in command_text:
                assert any("is not supported" in str(block) for block in blocks)

    @pytest.mark.parametrize(
        ("subcommand", "module_path"),
        [
            ("chapters", "apps.slack.commands.chapters.chapters_handler"),
            ("committees", "apps.slack.commands.committees.committees_handler"),
            ("contribute", "apps.slack.commands.contribute.contribute_handler"),
            ("gsoc", "apps.slack.commands.gsoc.gsoc_handler"),
            ("leaders", "apps.slack.commands.leaders.leaders_handler"),
            ("projects", "apps.slack.commands.projects.projects_handler"),
        ],
    )
    def test_owasp_subcommands(
        self,
        subcommand,
        module_path,
        mock_client,
        mock_command,
        mock_get_chapters,
        mock_get_committees,
        mock_get_projects,
    ):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = f"{subcommand} test"

        with patch(module_path) as mock_handler:

            def side_effect(ack, command, client):
                ack()
                blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "Test"}}]
                conversation = client.conversations_open(users=command["user_id"])
                client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)

            if subcommand in ["chapters", "committees", "projects"]:
                mock_handler.side_effect = side_effect

            owasp_handler(ack=MagicMock(), command=mock_command, client=mock_client)
            mock_handler.assert_called_once()
