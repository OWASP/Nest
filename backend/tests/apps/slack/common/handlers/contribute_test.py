from unittest.mock import patch

import pytest

from apps.slack.common.handlers.contribute import get_blocks
from apps.slack.common.presentation import EntityPresentation

EXPECTED_BUTTON_COUNT = 2


class TestContributeHandler:
    GET_PAGINATION_BUTTONS_PATH = "apps.slack.common.handlers.contribute.get_pagination_buttons"

    @pytest.fixture
    def mock_issue_data(self):
        return {
            "hits": [
                {
                    "idx_title": "Test Issue",
                    "idx_summary": "This is a test issue summary",
                    "idx_url": "https://example.com/issue",
                    "idx_project_name": "Test Project",
                    "idx_project_url": "https://example.com/project",
                }
            ],
            "nbPages": 2,
        }

    @pytest.fixture
    def mock_empty_issue_data(self):
        return {
            "hits": [],
            "nbPages": 0,
        }

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        with (
            patch("apps.owasp.api.search.issue.get_issues") as mock_get_issues,
            patch("apps.github.models.issue.Issue") as mock_issue_model,
        ):
            mock_issue_model.open_issues_count.return_value = 42
            yield {"get_issues": mock_get_issues, "issue_model": mock_issue_model}

    def test_get_blocks_with_results(self, setup_mocks, mock_issue_data):
        setup_mocks["get_issues"].return_value = mock_issue_data

        blocks = get_blocks()

        assert "Test Issue" in blocks[0]["text"]["text"]
        assert "Test Project" in blocks[0]["text"]["text"]
        assert "This is a test issue summary" in blocks[0]["text"]["text"]

    def test_get_blocks_no_results(self, setup_mocks, mock_empty_issue_data):
        setup_mocks["get_issues"].return_value = mock_empty_issue_data

        blocks = get_blocks(search_query="nonexistent")

        assert len(blocks) == 1
        assert "No issues found for" in blocks[0]["text"]["text"]

    def test_get_blocks_no_results_without_query(self, setup_mocks, mock_empty_issue_data):
        setup_mocks["get_issues"].return_value = mock_empty_issue_data

        blocks = get_blocks()

        assert len(blocks) == 1
        assert "No issues found" in blocks[0]["text"]["text"]
        assert "`" not in blocks[0]["text"]["text"]

    def test_feedback_message(self, setup_mocks, mock_issue_data):
        setup_mocks["get_issues"].return_value = mock_issue_data
        presentation = EntityPresentation(include_feedback=True)

        blocks = get_blocks(presentation=presentation)

        assert "Extended search over 42 OWASP issues" in blocks[-1]["text"]["text"]

    def test_pagination(self, setup_mocks, mock_issue_data):
        mock_issue_data["nbPages"] = 3
        setup_mocks["get_issues"].return_value = mock_issue_data
        presentation = EntityPresentation(include_pagination=True)

        with patch(self.GET_PAGINATION_BUTTONS_PATH) as mock_pagination:
            mock_pagination.return_value = [
                {"type": "button", "text": {"type": "plain_text", "text": "Next"}}
            ]
            blocks = get_blocks(page=1, presentation=presentation)
            assert mock_pagination.called
            assert blocks[-1]["type"] == "actions"

            mock_pagination.return_value = [
                {"type": "button", "text": {"type": "plain_text", "text": "Previous"}},
                {"type": "button", "text": {"type": "plain_text", "text": "Next"}},
            ]
            blocks = get_blocks(page=2, presentation=presentation)
            assert len(blocks[-1]["elements"]) == EXPECTED_BUTTON_COUNT
            assert mock_pagination.call_count == EXPECTED_BUTTON_COUNT

    def test_no_pagination_when_disabled(self, setup_mocks, mock_issue_data):
        mock_issue_data["nbPages"] = 3
        setup_mocks["get_issues"].return_value = mock_issue_data
        presentation = EntityPresentation(include_pagination=False)

        blocks = get_blocks(presentation=presentation)
        assert len(blocks) > 0
        assert all(block["type"] != "actions" for block in blocks)

    def test_pagination_empty(self, setup_mocks, mock_issue_data):
        mock_issue_data["nbPages"] = 1
        setup_mocks["get_issues"].return_value = mock_issue_data
        presentation = EntityPresentation(include_pagination=True)

        with patch(self.GET_PAGINATION_BUTTONS_PATH, return_value=[]):
            blocks = get_blocks(page=1, presentation=presentation)
            assert all(block["type"] != "actions" for block in blocks)

    def test_pagination_edge_case(self, setup_mocks, mock_issue_data):
        mock_issue_data["nbPages"] = 2
        setup_mocks["get_issues"].return_value = mock_issue_data
        presentation = EntityPresentation(include_pagination=True)

        with patch(self.GET_PAGINATION_BUTTONS_PATH) as mock_pagination:
            mock_pagination.return_value = None
            blocks = get_blocks(page=2, presentation=presentation)
            assert all(block["type"] != "actions" for block in blocks)
            assert mock_pagination.called
