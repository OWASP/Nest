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
