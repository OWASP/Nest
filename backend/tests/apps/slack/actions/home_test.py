from unittest.mock import MagicMock, patch

import pytest
from slack_sdk.errors import SlackApiError

from apps.slack.actions.home import handle_home_actions
from apps.slack.constants import (
    VIEW_CHAPTERS_ACTION,
    VIEW_COMMITTEES_ACTION,
    VIEW_CONTRIBUTE_ACTION,
    VIEW_PROJECTS_ACTION,
)


class TestHomeActions:
    @pytest.fixture
    def mock_client(self):
        return MagicMock()

    @pytest.fixture
    def mock_body(self):
        return {
            "user": {"id": "U123456"},
            "actions": [{"action_id": ""}],
        }

    @pytest.fixture(autouse=True)
    def _mock_external_calls(self):
        """Mock all external API calls."""
        with (
            patch("apps.owasp.index.search.project.get_projects") as mock_projects,
            patch("apps.owasp.index.search.chapter.get_chapters") as mock_chapters,
            patch("apps.owasp.index.search.committee.get_committees") as mock_committees,
            patch("apps.owasp.index.search.issue.get_issues") as mock_issues,
        ):
            mock_projects.return_value = {"hits": [], "nbPages": 1}
            mock_chapters.return_value = {"hits": [], "nbPages": 1}
            mock_committees.return_value = {"hits": [], "nbPages": 1}
            mock_issues.return_value = {"hits": [], "nbPages": 1}
            yield

    @pytest.mark.parametrize(
        ("action_id", "expected_blocks_length"),
        [
            (VIEW_PROJECTS_ACTION, 2),
            (VIEW_COMMITTEES_ACTION, 2),
            (VIEW_CHAPTERS_ACTION, 2),
            (VIEW_CONTRIBUTE_ACTION, 2),
            ("invalid_action", 2),
        ],
    )
    def test_handle_home_actions(self, mock_client, mock_body, action_id, expected_blocks_length):
        mock_body["actions"][0]["action_id"] = action_id

        handle_home_actions(MagicMock(), mock_body, mock_client)

        mock_client.views_publish.assert_called_once()
        view = mock_client.views_publish.call_args[1]["view"]
        assert len(view["blocks"]) >= expected_blocks_length
        assert view["type"] == "home"

    def test_handle_home_actions_api_error(self, mock_client, mock_body):
        mock_client.views_publish.side_effect = SlackApiError("Error", {"error": "test_error"})
        mock_body["actions"][0]["action_id"] = VIEW_PROJECTS_ACTION

        handle_home_actions(MagicMock(), mock_body, mock_client)
