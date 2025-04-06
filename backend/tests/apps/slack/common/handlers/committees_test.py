from unittest.mock import patch

import pytest

from apps.slack.common.handlers.committees import get_blocks
from apps.slack.common.presentation import EntityPresentation

PAGINATION_BUTTONS_PATH = "apps.slack.common.handlers.committees.get_pagination_buttons"


class TestCommitteeHandler:
    @pytest.fixture
    def mock_committee_data(self):
        return {
            "hits": [
                {
                    "idx_name": "Test Committee",
                    "idx_summary": "This is a test committee summary",
                    "idx_url": "https://example.com/committee",
                    "idx_leaders": ["John Doe", "Jane Smith"],
                }
            ],
            "nbPages": 2,
        }

    @pytest.fixture
    def mock_empty_committee_data(self):
        return {
            "hits": [],
            "nbPages": 0,
        }

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        with (
            patch("apps.owasp.api.search.committee.get_committees") as mock_get_committees,
            patch("apps.owasp.models.committee.Committee") as mock_committee_model,
        ):
            mock_committee_model.active_committees_count.return_value = 15
            yield {"get_committees": mock_get_committees, "committee_model": mock_committee_model}

    def test_get_blocks_with_results(self, setup_mocks, mock_committee_data):
        setup_mocks["get_committees"].return_value = mock_committee_data

        blocks = get_blocks(search_query="test")

        assert "OWASP committees that I found for" in blocks[0]["text"]["text"]
        assert "Test Committee" in blocks[1]["text"]["text"]
        assert "This is a test committee summary" in blocks[1]["text"]["text"]

    def test_get_blocks_no_results(self, setup_mocks, mock_empty_committee_data):
        setup_mocks["get_committees"].return_value = mock_empty_committee_data

        blocks = get_blocks(search_query="nonexistent")

        assert len(blocks) == 1
        assert "No committees found for" in blocks[0]["text"]["text"]

    def test_get_blocks_without_search_query(self, setup_mocks, mock_committee_data):
        setup_mocks["get_committees"].return_value = mock_committee_data

        blocks = get_blocks()

        assert "OWASP committees:" in blocks[0]["text"]["text"]

    def test_feedback_message(self, setup_mocks, mock_committee_data):
        setup_mocks["get_committees"].return_value = mock_committee_data
        presentation = EntityPresentation(include_feedback=True)

        blocks = get_blocks(presentation=presentation)

        assert "Extended search over 42 OWASP committees" in blocks[-1]["text"]["text"]

    def test_pagination(self, setup_mocks, mock_committee_data):
        mock_committee_data["nbPages"] = 3
        setup_mocks["get_committees"].return_value = mock_committee_data
        presentation = EntityPresentation(include_pagination=True)

        with patch(PAGINATION_BUTTONS_PATH) as mock_pagination:
            mock_pagination.return_value = [
                {"type": "button", "text": {"type": "plain_text", "text": "Next"}}
            ]
            blocks = get_blocks(page=1, presentation=presentation)
            assert mock_pagination.called
            assert blocks[-1]["type"] == "actions"

            expected_button_count = 2
            mock_pagination.return_value = [
                {"type": "button", "text": {"type": "plain_text", "text": "Previous"}},
                {"type": "button", "text": {"type": "plain_text", "text": "Next"}},
            ]
            blocks = get_blocks(page=2, presentation=presentation)
            assert len(blocks[-1]["elements"]) == expected_button_count
            assert mock_pagination.call_count == expected_button_count

    def test_no_pagination_when_disabled(self, setup_mocks, mock_committee_data):
        mock_committee_data["nbPages"] = 3
        setup_mocks["get_committees"].return_value = mock_committee_data
        presentation = EntityPresentation(include_pagination=False)

        blocks = get_blocks(presentation=presentation)
        assert blocks[-1]["type"] != "actions"

    def test_leaders_singular_plural(self, setup_mocks, mock_committee_data):
        with patch(PAGINATION_BUTTONS_PATH, return_value=[]):
            setup_mocks["get_committees"].return_value = mock_committee_data
            presentation = EntityPresentation(include_metadata=True)

            blocks = get_blocks(presentation=presentation)
            assert "Leaders: John Doe, Jane Smith" in blocks[1]["text"]["text"]

            mock_committee_data["hits"][0]["idx_leaders"] = ["John Doe"]
            setup_mocks["get_committees"].return_value = mock_committee_data

            blocks = get_blocks(presentation=presentation)
            assert "Leader: John Doe" in blocks[1]["text"]["text"]

            mock_committee_data["hits"][0]["idx_leaders"] = []
            setup_mocks["get_committees"].return_value = mock_committee_data

            blocks = get_blocks(presentation=presentation)
            assert "Leader" not in blocks[1]["text"]["text"]

    def test_pagination_empty(self, setup_mocks, mock_committee_data):
        mock_committee_data["nbPages"] = 1
        setup_mocks["get_committees"].return_value = mock_committee_data
        presentation = EntityPresentation(include_pagination=True)

        with patch(PAGINATION_BUTTONS_PATH, return_value=[]):
            blocks = get_blocks(page=1, presentation=presentation)
            assert all(block["type"] != "actions" for block in blocks)

    def test_pagination_edge_case(self, setup_mocks, mock_committee_data):
        mock_committee_data["nbPages"] = 2
        setup_mocks["get_committees"].return_value = mock_committee_data
        presentation = EntityPresentation(include_pagination=True)

        with patch(PAGINATION_BUTTONS_PATH) as mock_pagination:
            mock_pagination.return_value = None
            blocks = get_blocks(page=2, presentation=presentation)
            assert all(block["type"] != "actions" for block in blocks)
            assert mock_pagination.called
