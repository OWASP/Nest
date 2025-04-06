from unittest.mock import MagicMock, patch

import pytest
from slack_sdk.errors import SlackApiError

from apps.slack.actions.home import handle_home_actions
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

PAGE_NUMBER = 2
MIN_ACTION_CALLS = 12


class TestHomeActions:
    @pytest.fixture
    def mock_client(self):
        return MagicMock()

    @pytest.fixture
    def mock_ack(self):
        return MagicMock()

    @pytest.fixture
    def mock_body_template(self):
        return {
            "user": {"id": "U12345"},
            "actions": [{"action_id": VIEW_CHAPTERS_ACTION, "value": "1"}],
        }

    @pytest.fixture
    def mock_body(self):
        return {
            "user": {"id": "U67890"},
            "actions": [{"action_id": VIEW_PROJECTS_ACTION, "value": "3"}],
        }

    @pytest.mark.parametrize(
        ("action_id", "expected_handler"),
        [
            (VIEW_CHAPTERS_ACTION, "apps.slack.common.handlers.chapters.get_blocks"),
            (VIEW_CHAPTERS_ACTION_NEXT, "apps.slack.common.handlers.chapters.get_blocks"),
            (VIEW_CHAPTERS_ACTION_PREV, "apps.slack.common.handlers.chapters.get_blocks"),
            (VIEW_COMMITTEES_ACTION, "apps.slack.common.handlers.committees.get_blocks"),
            (VIEW_COMMITTEES_ACTION_NEXT, "apps.slack.common.handlers.committees.get_blocks"),
            (VIEW_COMMITTEES_ACTION_PREV, "apps.slack.common.handlers.committees.get_blocks"),
            (VIEW_PROJECTS_ACTION, "apps.slack.common.handlers.projects.get_blocks"),
            (VIEW_PROJECTS_ACTION_NEXT, "apps.slack.common.handlers.projects.get_blocks"),
            (VIEW_PROJECTS_ACTION_PREV, "apps.slack.common.handlers.projects.get_blocks"),
            (VIEW_CONTRIBUTE_ACTION, "apps.slack.common.handlers.contribute.get_blocks"),
            (VIEW_CONTRIBUTE_ACTION_NEXT, "apps.slack.common.handlers.contribute.get_blocks"),
            (VIEW_CONTRIBUTE_ACTION_PREV, "apps.slack.common.handlers.contribute.get_blocks"),
        ],
    )
    def test_handle_home_actions(
        self, mock_ack, mock_client, mock_body_template, action_id, expected_handler
    ):
        mock_body = dict(mock_body_template)
        mock_body["actions"] = [{"action_id": action_id, "value": "2"}]

        with patch(expected_handler, return_value=[{"type": "section"}]) as mock_get_blocks:
            handle_home_actions(ack=mock_ack, body=mock_body, client=mock_client)

            mock_ack.assert_called_once()
            mock_get_blocks.assert_called_once()
            mock_client.views_publish.assert_called_once()

            _, kwargs = mock_get_blocks.call_args
            assert kwargs.get("page") == PAGE_NUMBER

            _, publish_kwargs = mock_client.views_publish.call_args
            assert publish_kwargs["user_id"] == "U67890"
            assert "blocks" in publish_kwargs["view"]

    def test_handle_home_actions_invalid_value(self, mock_ack, mock_client, mock_body_template):
        mock_body = dict(mock_body_template)
        mock_body["actions"] = [{"action_id": VIEW_PROJECTS_ACTION, "value": "invalid"}]

        with patch(
            "apps.slack.common.handlers.chapters.get_blocks", return_value=[{"type": "section"}]
        ) as mock_get_blocks:
            handle_home_actions(ack=mock_ack, body=mock_body, client=mock_client)

            mock_get_blocks.assert_called_once()
            _, kwargs = mock_get_blocks.call_args
            assert kwargs.get("page") == 1

    def test_handle_home_actions_unknown_action(self, mock_ack, mock_client, mock_body_template):
        mock_body = dict(mock_body_template)
        mock_body["actions"] = [{"action_id": "unknown_action", "value": "1"}]

        handle_home_actions(ack=mock_ack, body=mock_body, client=mock_client)

        mock_client.views_publish.assert_called_once()
        blocks = mock_client.views_publish.call_args[1]["view"]["blocks"]

        error_block = next(block for block in blocks if block.get("type") == "section")
        assert "Invalid action" in error_block["text"]["text"]

    def test_handle_home_actions_api_error(self, mock_ack, mock_client, mock_body_template):
        mock_body = dict(mock_body_template)
        mock_client.views_publish.side_effect = SlackApiError("Error", {"error": "test_error"})

        with (
            patch(
                "apps.slack.common.handlers.chapters.get_blocks",
                return_value=[{"type": "section"}],
            ),
            patch("apps.slack.actions.home.logger") as mock_logger,
        ):
            handle_home_actions(ack=mock_ack, body=mock_body, client=mock_client)
            mock_logger.exception.assert_called_once()

    def test_action_registration(self):
        from apps.slack.actions.home import SlackConfig

        with patch.object(SlackConfig, "app") as mock_app:
            import importlib

            from apps.slack import actions

            importlib.reload(actions.home)

            assert mock_app.action.call_count >= MIN_ACTION_CALLS
