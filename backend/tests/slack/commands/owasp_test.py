from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.owasp import COMMAND, owasp_handler


class TestOwaspHandler:
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

    @pytest.fixture()
    def mock_get_chapters(self):
        with patch("apps.owasp.api.search.chapter.get_chapters") as mock:
            mock.return_value = {"hits": []}
            yield mock

    @pytest.fixture()
    def mock_get_committees(self):
        with patch("apps.owasp.api.search.committee.get_committees") as mock:
            mock.return_value = {"hits": []}
            yield mock

    @pytest.fixture()
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

    @pytest.fixture()
    def mock_slack_command(self):
        return {
            "user_id": "U123456",
            "text": "",
        }

    @pytest.fixture()
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    def test_handler_disabled(self, mock_slack_command, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = False

        owasp_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        mock_slack_client.conversations_open.assert_not_called()
        mock_slack_client.chat_postMessage.assert_not_called()

    def test_handler_help(self, mock_slack_command, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True

        owasp_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        mock_slack_client.conversations_open.assert_called_once_with(
            users=mock_slack_command["user_id"]
        )
        mock_slack_client.chat_postMessage.assert_called_once()

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        text = blocks[0]["text"]["text"]

        assert "board" in text
        assert "chapters" in text
        assert "committees" in text
        assert "users" in text

    @patch("apps.slack.commands.board.board_handler")
    def test_handler_board(self, mock_board_handler, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "board some params"}

        owasp_handler(ack=MagicMock(), command=command.copy(), client=mock_slack_client)

        mock_board_handler.assert_called_once()
        assert mock_board_handler.call_args[0][1]["text"] == "some params"

    @patch("apps.slack.commands.chapters.chapters_handler")
    def test_handler_chapters(self, mock_handler, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "chapters some params"}

        owasp_handler(ack=MagicMock(), command=command.copy(), client=mock_slack_client)

        mock_handler.assert_called_once()
        assert mock_handler.call_args[0][1]["text"] == "some params"

    @patch("apps.slack.commands.committees.committees_handler")
    def test_handler_committees(self, mock_handler, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "committees some params"}

        owasp_handler(ack=MagicMock(), command=command.copy(), client=mock_slack_client)

        mock_handler.assert_called_once()
        assert mock_handler.call_args[0][1]["text"] == "some params"

    @patch("apps.slack.commands.community.community_handler")
    def test_handler_community(self, mock_handler, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "community some params"}

        owasp_handler(ack=MagicMock(), command=command.copy(), client=mock_slack_client)

        mock_handler.assert_called_once()
        assert mock_handler.call_args[0][1]["text"] == "some params"

    @patch("apps.slack.commands.contact.contact_handler")
    def test_handler_contact(self, mock_handler, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "contact some params"}

        owasp_handler(ack=MagicMock(), command=command.copy(), client=mock_slack_client)

        mock_handler.assert_called_once()
        assert mock_handler.call_args[0][1]["text"] == "some params"

    @patch("apps.slack.commands.contribute.contribute_handler")
    def test_handler_contribute(self, mock_handler, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "contribute some params"}

        owasp_handler(ack=MagicMock(), command=command.copy(), client=mock_slack_client)

        mock_handler.assert_called_once()
        assert mock_handler.call_args[0][1]["text"] == "some params"

    @patch("apps.slack.commands.donate.donate_handler")
    def test_handler_donate(self, mock_handler, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "donate some params"}

        owasp_handler(ack=MagicMock(), command=command.copy(), client=mock_slack_client)

        mock_handler.assert_called_once()
        assert mock_handler.call_args[0][1]["text"] == "some params"

    @patch("apps.slack.commands.events.events_handler")
    def test_handler_events(self, mock_handler, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "events some params"}

        owasp_handler(ack=MagicMock(), command=command.copy(), client=mock_slack_client)

        mock_handler.assert_called_once()
        assert mock_handler.call_args[0][1]["text"] == "some params"

    @patch("apps.slack.commands.gsoc.gsoc_handler")
    def test_handler_gsoc(self, mock_handler, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "gsoc some params"}

        owasp_handler(ack=MagicMock(), command=command.copy(), client=mock_slack_client)

        mock_handler.assert_called_once()
        assert mock_handler.call_args[0][1]["text"] == "some params"

    @patch("apps.slack.commands.jobs.jobs_handler")
    def test_handler_jobs(self, mock_handler, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "jobs some params"}

        owasp_handler(ack=MagicMock(), command=command.copy(), client=mock_slack_client)

        mock_handler.assert_called_once()
        assert mock_handler.call_args[0][1]["text"] == "some params"

    @patch("apps.slack.commands.leaders.leaders_handler")
    def test_handler_leaders(self, mock_handler, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "leaders some params"}

        owasp_handler(ack=MagicMock(), command=command.copy(), client=mock_slack_client)

        mock_handler.assert_called_once()
        assert mock_handler.call_args[0][1]["text"] == "some params"

    @patch("apps.slack.commands.news.news_handler")
    def test_handler_news(self, mock_handler, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "news some params"}

        owasp_handler(ack=MagicMock(), command=command.copy(), client=mock_slack_client)

        mock_handler.assert_called_once()
        assert mock_handler.call_args[0][1]["text"] == "some params"

    @patch("apps.slack.commands.projects.projects_handler")
    def test_handler_projects(self, mock_handler, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "projects some params"}

        owasp_handler(ack=MagicMock(), command=command.copy(), client=mock_slack_client)

        mock_handler.assert_called_once()
        assert mock_handler.call_args[0][1]["text"] == "some params"

    @patch("apps.slack.commands.sponsor.sponsor_handler")
    def test_handler_sponsor(self, mock_handler, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "sponsor some params"}

        owasp_handler(ack=MagicMock(), command=command.copy(), client=mock_slack_client)

        mock_handler.assert_called_once()
        assert mock_handler.call_args[0][1]["text"] == "some params"

    @patch("apps.slack.commands.sponsors.sponsors_handler")
    def test_handler_sponsors(self, mock_handler, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "sponsors some params"}

        owasp_handler(ack=MagicMock(), command=command.copy(), client=mock_slack_client)

        mock_handler.assert_called_once()
        assert mock_handler.call_args[0][1]["text"] == "some params"

    @patch("apps.slack.commands.staff.staff_handler")
    def test_handler_staff(self, mock_handler, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "staff some params"}

        owasp_handler(ack=MagicMock(), command=command.copy(), client=mock_slack_client)

        mock_handler.assert_called_once()
        assert mock_handler.call_args[0][1]["text"] == "some params"

    @patch("apps.slack.commands.users.users_handler")
    def test_handler_users(self, mock_handler, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "users some params"}

        owasp_handler(ack=MagicMock(), command=command.copy(), client=mock_slack_client)

        mock_handler.assert_called_once()
        assert mock_handler.call_args[0][1]["text"] == "some params"

    def test_handler_unknown_command(self, mock_slack_client):
        settings.SLACK_COMMANDS_ENABLED = True
        command = {"user_id": "U123456", "text": "unknown command"}

        owasp_handler(ack=MagicMock(), command=command, client=mock_slack_client)

        mock_slack_client.conversations_open.assert_called_once_with(users=command["user_id"])
        mock_slack_client.chat_postMessage.assert_called_once()

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        assert "is not supported" in blocks[0]["text"]["text"]

    @patch("apps.slack.apps.SlackConfig.app")
    def test_command_registration(self, mock_app):
        import importlib

        from apps.slack.commands import owasp

        mock_command_decorator = MagicMock()
        mock_app.command.return_value = mock_command_decorator

        importlib.reload(owasp)

        mock_app.command.assert_called_once_with(COMMAND)
        assert mock_command_decorator.call_count == 1
        assert mock_command_decorator.call_args[0][0].__name__ == "owasp_handler"
