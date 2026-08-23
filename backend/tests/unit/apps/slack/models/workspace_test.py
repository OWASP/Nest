import os
from unittest.mock import patch

from apps.slack.models.workspace import Workspace


class TestWorkspaceModel:
    def test_bot_token(self):
        workspace_id = "T123ABC"
        expected_token = "xoxb-test-token"  # noqa: S105
        with patch.dict(os.environ, {f"SLACK_BOT_TOKEN_{workspace_id.upper()}": expected_token}):
            workspace = Workspace(slack_workspace_id=workspace_id)

            assert workspace.bot_token == expected_token

    def test_str(self):
        workspace = Workspace(name="Test Workspace", slack_workspace_id="test-workspace")

        assert str(workspace) == "Test Workspace"

    def test_bot_token_not_set(self):
        """Test bot_token returns empty string when environment variable is not set."""
        workspace = Workspace(slack_workspace_id="NONEXISTENT")
        with patch.dict(os.environ, {}, clear=True):
            assert workspace.bot_token == ""

    def test_get_default_workspace_not_found(self):
        """Test get_default_workspace returns None when default workspace doesn't exist."""
        with patch.object(Workspace.objects, "filter") as mock_filter:
            mock_filter.return_value.first.return_value = None

            result = Workspace.get_default_workspace()

            assert result is None

    def test_invite_link_alert_threshold_none_when_baseline_unset(self):
        """Threshold is undefined until invite_link_member_count is set."""
        workspace = Workspace(
            slack_workspace_id="T_THRESH",
            invite_link_member_count=None,
        )

        assert workspace.invite_link_alert_threshold is None

    def test_invite_link_alert_threshold_uses_350_when_offset_null(self):
        """Restored rows may have NULL offset; logic matches model default of 350."""
        workspace = Workspace(
            slack_workspace_id="T_THRESH",
            invite_link_member_count=100,
            invite_link_alert_member_offset=None,
        )

        assert workspace.invite_link_alert_threshold == 450

    def test_invite_link_alert_threshold_with_explicit_offset(self):
        workspace = Workspace(
            slack_workspace_id="T_THRESH",
            invite_link_member_count=50,
            invite_link_alert_member_offset=10,
        )

        assert workspace.invite_link_alert_threshold == 60

    def test_is_content_reporting_enabled(self):
        """Content reporting requires a non-empty alert channel id."""
        assert (
            Workspace(
                slack_workspace_id="T1",
                content_report_alert_channel_id="C_ALERT",
            ).is_content_reporting_enabled
            is True
        )
        assert (
            Workspace(
                slack_workspace_id="T1",
                content_report_alert_channel_id="",
            ).is_content_reporting_enabled
            is False
        )
        assert (
            Workspace(
                slack_workspace_id="T1",
                content_report_alert_channel_id="   ",
            ).is_content_reporting_enabled
            is False
        )

    def test_get_by_workspace_id(self, mocker):
        """Lookup returns the matching workspace, or None when missing."""
        workspace = Workspace(slack_workspace_id="T1")
        manager = mocker.patch("apps.slack.models.workspace.Workspace.objects")
        manager.filter.return_value.first.return_value = workspace

        assert Workspace.get_by_workspace_id("T1") is workspace
        manager.filter.assert_called_once_with(slack_workspace_id="T1")

        manager.filter.return_value.first.return_value = None
        assert Workspace.get_by_workspace_id("T_MISSING") is None
