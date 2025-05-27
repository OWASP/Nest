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
