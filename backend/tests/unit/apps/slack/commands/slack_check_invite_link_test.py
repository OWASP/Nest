"""Tests for slack_check_invite_link management command."""

from datetime import UTC, datetime
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone
from github.GithubException import GithubException
from slack_sdk.errors import SlackApiError

from apps.github.constants import OWASP_GITHUB_IO, OWASP_LOGIN
from apps.slack.constants import OWASP_WORKSPACE_ID
from apps.slack.management.commands.slack_check_invite_link import (
    ERR_INVITE_BASELINE_UNSET,
)
from apps.slack.management.commands.slack_check_invite_link import (
    Command as SlackCheckInviteLinkCommand,
)
from apps.slack.models import Workspace

TEST_TOKEN = "xoxb-test-token"  # noqa: S105


class FakeWorkspace:
    """In-memory workspace for command tests (no DB)."""

    def __init__(self):
        self.slack_workspace_id = OWASP_WORKSPACE_ID
        self.total_members_count = 0
        self.invite_link_created_at = None
        self.invite_link_commit_sha = ""
        self.invite_link_member_count = None
        self.invite_link_last_alert_sent_at = None
        self.invite_link_alert_channel_id = ""
        self.invite_link_alert_user_ids = []
        self.invite_link_alert_member_offset = 350
        self._bot_token = TEST_TOKEN

    @property
    def invite_link_alert_threshold(self):
        if self.invite_link_member_count is None:
            return None
        offset = (
            self.invite_link_alert_member_offset
            if self.invite_link_alert_member_offset is not None
            else 350
        )
        return self.invite_link_member_count + offset

    @property
    def bot_token(self):
        return self._bot_token

    def save(self, update_fields=None):
        """No-op: fake is in-memory only; the command mutates attributes directly."""

    def refresh_from_db(self):
        """No-op: there is no database row; tests read attributes already set on this instance."""


@pytest.fixture
def fake_workspace():
    return FakeWorkspace()


class TestSlackCheckInviteLinkCommand:
    """Test cases for slack_check_invite_link."""

    @patch.object(Workspace, "get_default_workspace")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_latest_invite_link_commit")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_github_client")
    def test_sets_baseline_when_invite_link_commit_found(
        self,
        mock_gh_client,
        mock_commit_at,
        mock_get_workspace,
        fake_workspace,
    ):
        commit_sha = "a" * 40
        mock_get_workspace.return_value = fake_workspace
        mock_commit_at.return_value = (datetime(2025, 1, 1, tzinfo=UTC), commit_sha)
        fake_workspace.total_members_count = 100
        call_command("slack_check_invite_link")
        assert fake_workspace.invite_link_created_at == datetime(2025, 1, 1, tzinfo=UTC)
        assert fake_workspace.invite_link_commit_sha == commit_sha
        assert fake_workspace.invite_link_member_count == 100
        assert fake_workspace.invite_link_alert_threshold == 450

    @patch.object(Workspace, "get_default_workspace")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_latest_invite_link_commit")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_github_client")
    def test_baseline_not_set_without_github_commit_or_metadata(
        self,
        mock_gh_client,
        mock_commit_at,
        mock_get_workspace,
        fake_workspace,
    ):
        mock_get_workspace.return_value = fake_workspace
        mock_commit_at.return_value = (None, None)
        fake_workspace.total_members_count = 100
        call_command("slack_check_invite_link")
        assert fake_workspace.invite_link_member_count is None

    @patch.object(Workspace, "get_default_workspace")
    @patch("apps.slack.management.commands.slack_check_invite_link.WebClient")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_latest_invite_link_commit")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_github_client")
    def test_posts_alert_when_at_threshold(
        self,
        mock_gh_client,
        mock_commit_at,
        mock_web_client_class,
        mock_get_workspace,
        fake_workspace,
    ):
        mock_get_workspace.return_value = fake_workspace
        commit_time = datetime(2025, 1, 1, tzinfo=UTC)
        commit_sha = "b" * 40
        mock_commit_at.return_value = (commit_time, commit_sha)
        fake_workspace.total_members_count = 500
        mock_client = MagicMock()
        mock_web_client_class.return_value = mock_client

        fake_workspace.invite_link_created_at = commit_time
        fake_workspace.invite_link_commit_sha = commit_sha
        fake_workspace.invite_link_member_count = 100
        fake_workspace.invite_link_last_alert_sent_at = None
        fake_workspace.invite_link_alert_channel_id = "C01234567"

        call_command("slack_check_invite_link")

        mock_client.chat_postMessage.assert_called_once()
        posted = mock_client.chat_postMessage.call_args[1]["text"]
        assert (
            f"<https://github.com/{OWASP_LOGIN}/{OWASP_GITHUB_IO}/commit/{commit_sha}|"
            f"{commit_time.date().isoformat()}>"
        ) in posted
        assert fake_workspace.invite_link_last_alert_sent_at is not None

    @patch.object(Workspace, "get_default_workspace")
    @patch("apps.slack.management.commands.slack_check_invite_link.WebClient")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_latest_invite_link_commit")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_github_client")
    def test_posts_alert_trailing_cc_line_when_user_ids_configured(
        self,
        mock_gh_client,
        mock_commit_at,
        mock_web_client_class,
        mock_get_workspace,
        fake_workspace,
    ):
        mock_get_workspace.return_value = fake_workspace
        commit_time = datetime(2025, 1, 1, tzinfo=UTC)
        commit_sha = "b" * 40
        mock_commit_at.return_value = (commit_time, commit_sha)
        fake_workspace.total_members_count = 500
        mock_client = MagicMock()
        mock_web_client_class.return_value = mock_client

        fake_workspace.invite_link_created_at = commit_time
        fake_workspace.invite_link_commit_sha = commit_sha
        fake_workspace.invite_link_member_count = 100
        fake_workspace.invite_link_last_alert_sent_at = None
        fake_workspace.invite_link_alert_channel_id = "C01234567"
        fake_workspace.invite_link_alert_user_ids = ["U0123ABCD", "U9876ZYXW"]

        call_command("slack_check_invite_link")

        mock_client.chat_postMessage.assert_called_once()
        posted = mock_client.chat_postMessage.call_args[1]["text"]
        assert posted.endswith("\n\ncc: <@U0123ABCD> <@U9876ZYXW>")

    @patch.object(Workspace, "get_default_workspace")
    @patch("apps.slack.management.commands.slack_check_invite_link.WebClient")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_latest_invite_link_commit")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_github_client")
    def test_sets_baseline_when_created_at_exists_but_member_count_unset(
        self,
        mock_gh_client,
        mock_commit_at,
        mock_web_client_class,
        mock_get_workspace,
        fake_workspace,
    ):
        mock_get_workspace.return_value = fake_workspace
        mock_commit_at.return_value = (None, None)
        commit_time = datetime(2025, 6, 1, tzinfo=UTC)
        fake_workspace.invite_link_created_at = commit_time
        fake_workspace.invite_link_commit_sha = "d" * 40
        fake_workspace.total_members_count = 1000
        mock_web_client_class.return_value = MagicMock()

        call_command("slack_check_invite_link")

        assert fake_workspace.invite_link_member_count == 1000
        assert fake_workspace.invite_link_alert_threshold == 1350
        assert fake_workspace.invite_link_last_alert_sent_at is None

    @patch.object(Workspace, "get_default_workspace")
    def test_raises_when_no_default_workspace(self, mock_get_workspace):
        mock_get_workspace.return_value = None
        with pytest.raises(CommandError, match="Default OWASP Slack workspace"):
            call_command("slack_check_invite_link")

    @patch.object(Workspace, "get_default_workspace")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_latest_invite_link_commit")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_github_client")
    def test_raises_when_bot_token_missing(
        self,
        mock_gh_client,
        mock_commit_at,
        mock_get_workspace,
        fake_workspace,
    ):
        mock_get_workspace.return_value = fake_workspace
        fake_workspace._bot_token = ""
        mock_commit_at.return_value = (None, None)
        with pytest.raises(CommandError, match="No SLACK_BOT_TOKEN_"):
            call_command("slack_check_invite_link")

    def test_alert_raises_when_baseline_unset(self, fake_workspace):
        """Direct alert() call with no member baseline (threshold None)."""
        fake_workspace.invite_link_member_count = None
        cmd = SlackCheckInviteLinkCommand()
        with pytest.raises(CommandError, match=ERR_INVITE_BASELINE_UNSET):
            cmd.alert(fake_workspace, current_members=100)

    @patch.object(Workspace, "get_default_workspace")
    @patch("apps.slack.management.commands.slack_check_invite_link.WebClient")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_latest_invite_link_commit")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_github_client")
    def test_writes_ok_when_below_threshold(
        self,
        mock_gh_client,
        mock_commit_at,
        mock_web_client_class,
        mock_get_workspace,
        fake_workspace,
    ):
        mock_get_workspace.return_value = fake_workspace
        commit_time = datetime(2025, 1, 1, tzinfo=UTC)
        commit_sha = "c" * 40
        mock_commit_at.return_value = (commit_time, commit_sha)
        fake_workspace.total_members_count = 200
        fake_workspace.invite_link_created_at = commit_time
        fake_workspace.invite_link_commit_sha = commit_sha
        fake_workspace.invite_link_member_count = 100
        mock_web_client_class.return_value = MagicMock()

        out = StringIO()
        call_command("slack_check_invite_link", stdout=out)

        assert "OK: current=200, threshold=450" in out.getvalue()
        mock_web_client_class.return_value.chat_postMessage.assert_not_called()

    @patch.object(Workspace, "get_default_workspace")
    @patch("apps.slack.management.commands.slack_check_invite_link.WebClient")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_latest_invite_link_commit")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_github_client")
    def test_skips_second_alert_when_first_already_sent(
        self,
        mock_gh_client,
        mock_commit_at,
        mock_web_client_class,
        mock_get_workspace,
        fake_workspace,
    ):
        mock_get_workspace.return_value = fake_workspace
        commit_time = datetime(2025, 1, 1, tzinfo=UTC)
        commit_sha = "d" * 40
        mock_commit_at.return_value = (commit_time, commit_sha)
        fake_workspace.total_members_count = 500
        mock_web_client_class.return_value = MagicMock()

        fake_workspace.invite_link_created_at = commit_time
        fake_workspace.invite_link_commit_sha = commit_sha
        fake_workspace.invite_link_member_count = 100
        fake_workspace.invite_link_last_alert_sent_at = timezone.now()
        fake_workspace.invite_link_alert_channel_id = "C01234567"

        out = StringIO()
        call_command("slack_check_invite_link", stdout=out)

        assert "Threshold already reached" in out.getvalue()
        mock_web_client_class.return_value.chat_postMessage.assert_not_called()

    @patch.object(Workspace, "get_default_workspace")
    @patch("apps.slack.management.commands.slack_check_invite_link.WebClient")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_latest_invite_link_commit")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_github_client")
    def test_alert_fails_gracefully_when_channel_id_empty(
        self,
        mock_gh_client,
        mock_commit_at,
        mock_web_client_class,
        mock_get_workspace,
        fake_workspace,
    ):
        mock_get_workspace.return_value = fake_workspace
        commit_time = datetime(2025, 1, 1, tzinfo=UTC)
        commit_sha = "e" * 40
        mock_commit_at.return_value = (commit_time, commit_sha)
        fake_workspace.total_members_count = 500
        mock_web_client_class.return_value = MagicMock()

        fake_workspace.invite_link_created_at = commit_time
        fake_workspace.invite_link_commit_sha = commit_sha
        fake_workspace.invite_link_member_count = 100
        fake_workspace.invite_link_last_alert_sent_at = None
        fake_workspace.invite_link_alert_channel_id = ""

        out = StringIO()
        call_command("slack_check_invite_link", stdout=out)

        assert "invite_link_alert_channel_id is empty" in out.getvalue()
        mock_web_client_class.return_value.chat_postMessage.assert_not_called()

    @patch.object(Workspace, "get_default_workspace")
    @patch("apps.slack.management.commands.slack_check_invite_link.WebClient")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_latest_invite_link_commit")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_github_client")
    def test_raises_command_error_on_slack_post_failure(
        self,
        mock_gh_client,
        mock_commit_at,
        mock_web_client_class,
        mock_get_workspace,
        fake_workspace,
    ):
        mock_get_workspace.return_value = fake_workspace
        commit_time = datetime(2025, 1, 1, tzinfo=UTC)
        commit_sha = "f" * 40
        mock_commit_at.return_value = (commit_time, commit_sha)
        fake_workspace.total_members_count = 500
        mock_client = MagicMock()
        mock_client.chat_postMessage.side_effect = SlackApiError(
            message="post failed",
            response={"error": "channel_not_found"},
        )
        mock_web_client_class.return_value = mock_client

        fake_workspace.invite_link_created_at = commit_time
        fake_workspace.invite_link_commit_sha = commit_sha
        fake_workspace.invite_link_member_count = 100
        fake_workspace.invite_link_last_alert_sent_at = None
        fake_workspace.invite_link_alert_channel_id = "C01234567"

        with pytest.raises(
            CommandError,
            match=r"Slack chat\.postMessage error: channel_not_found",
        ):
            call_command("slack_check_invite_link")

    @patch.object(Workspace, "get_default_workspace")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_latest_invite_link_commit")
    @patch("apps.slack.management.commands.slack_check_invite_link.get_github_client")
    def test_raises_command_error_on_github_exception(
        self,
        mock_gh_client,
        mock_commit_at,
        mock_get_workspace,
        fake_workspace,
    ):
        mock_get_workspace.return_value = fake_workspace
        mock_gh_client.side_effect = GithubException(403, {}, {"message": "API rate limit"})
        fake_workspace.invite_link_created_at = datetime(2025, 1, 1, tzinfo=UTC)
        fake_workspace.invite_link_commit_sha = "a" * 40
        fake_workspace.total_members_count = 100
        fake_workspace.invite_link_member_count = 50

        with pytest.raises(CommandError, match="GitHub API error"):
            call_command("slack_check_invite_link")
        mock_commit_at.assert_not_called()


class TestInviteLinkAlertCcLine:
    """Unit tests for invite_link_alert_cc_line helper."""

    def test_empty_when_not_a_list(self):
        cmd = SlackCheckInviteLinkCommand()
        assert cmd.invite_link_alert_cc_line(None) == ""
        assert cmd.invite_link_alert_cc_line("U123") == ""
        assert cmd.invite_link_alert_cc_line({}) == ""

    def test_empty_when_list_has_only_blank_ids(self):
        cmd = SlackCheckInviteLinkCommand()
        assert cmd.invite_link_alert_cc_line(["", ""]) == ""
