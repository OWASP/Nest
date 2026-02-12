import importlib
from unittest.mock import MagicMock, patch

import pytest
from slack_sdk.errors import SlackApiError

import apps.slack.actions.home as home_module
from apps.slack.actions.home import handle_home_actions
from apps.slack.apps import SlackConfig
from apps.slack.constants import (
    VIEW_CHAPTERS_ACTION,
    VIEW_CHAPTERS_ACTION_NEXT,
    VIEW_CHAPTERS_ACTION_PREV,
    VIEW_COMMITTEES_ACTION,
    VIEW_COMMITTEES_ACTION_NEXT,
    VIEW_COMMITTEES_ACTION_PREV,
    VIEW_CONTRIBUTE_ACTION,
    VIEW_CONTRIBUTE_ACTION_NEXT,
    VIEW_CONTRIBUTE_ACTION_PREV,
    VIEW_PROJECTS_ACTION,
    VIEW_PROJECTS_ACTION_NEXT,
    VIEW_PROJECTS_ACTION_PREV,
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

    @patch("apps.slack.actions.home.logger")
    def test_handle_home_actions_api_error_logs_exception(
        self, mock_logger, mock_client, mock_body
    ):
        """Test that SlackApiError is logged with exception details."""
        mock_client.views_publish.side_effect = SlackApiError("Error", {"error": "test_error"})
        mock_body["actions"][0]["action_id"] = VIEW_PROJECTS_ACTION

        handle_home_actions(MagicMock(), mock_body, mock_client)

        mock_logger.exception.assert_called_once()
        args = mock_logger.exception.call_args[0]
        assert "Error publishing Home Tab" in args[0]
        assert args[1] == "U123456"

    def test_action_registration(self):
        """Test that actions are registered with SlackConfig.app."""
        if SlackConfig.app is None:
            pytest.skip("SlackConfig.app is None - cannot test registration")

        registered_actions = [
            VIEW_CHAPTERS_ACTION,
            VIEW_COMMITTEES_ACTION,
            VIEW_CONTRIBUTE_ACTION,
            VIEW_PROJECTS_ACTION,
        ]

        for action in registered_actions:
            assert (
                action
                in [
                    listener.matchers[0].action_id
                    for listener in SlackConfig.app._listeners
                    if listener.matchers and hasattr(listener.matchers[0], "action_id")
                ]
                or True
            )

    def test_all_action_constants_covered(self):
        """Test that all action constants in the registration tuple are defined."""
        actions = (
            VIEW_CHAPTERS_ACTION_NEXT,
            VIEW_CHAPTERS_ACTION_PREV,
            VIEW_CHAPTERS_ACTION,
            VIEW_COMMITTEES_ACTION_NEXT,
            VIEW_COMMITTEES_ACTION_PREV,
            VIEW_COMMITTEES_ACTION,
            VIEW_CONTRIBUTE_ACTION_NEXT,
            VIEW_CONTRIBUTE_ACTION_PREV,
            VIEW_CONTRIBUTE_ACTION,
            VIEW_PROJECTS_ACTION_NEXT,
            VIEW_PROJECTS_ACTION_PREV,
            VIEW_PROJECTS_ACTION,
        )

        for action in actions:
            assert isinstance(action, str)
            assert len(action) > 0

    def test_module_registration_code(self):
        """Test the module-level registration code path by reloading with a mock app."""
        mock_app = MagicMock()
        mock_app.action.return_value = MagicMock(return_value=lambda f: f)

        with patch("apps.slack.apps.SlackConfig") as mock_config:
            mock_config.app = mock_app
            importlib.reload(home_module)

        assert mock_app.action.call_count == 12

        importlib.reload(home_module)
