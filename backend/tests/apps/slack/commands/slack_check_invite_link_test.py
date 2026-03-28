"""Tests for slack_check_invite_link management command."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command

from apps.github.constants import OWASP_GITHUB_IO, OWASP_LOGIN
from apps.slack.constants import OWASP_WORKSPACE_ID
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

    @property
    def invite_link_alert_threshold(self):
        if self.invite_link_member_count is None:
            return None
        return self.invite_link_member_count + self.invite_link_alert_member_offset

    @property
    def bot_token(self):
        return TEST_TOKEN

    def save(self, update_fields=None):
        pass

    def refresh_from_db(self):
        pass


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
