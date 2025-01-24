from unittest.mock import patch

import pytest

from apps.slack.handlers.committees import committees_blocks


class TestCommitteesHandler:
    @pytest.fixture()
    def mock_committee(self):
        return {
            "idx_name": "Test Committee",
            "idx_summary": "Test Committee Summary",
            "idx_url": "http://example.com/committee/1",
            "idx_leaders": ["Leader 1", "Leader 2"],
        }

    @pytest.mark.parametrize(
        ("search_query", "has_results", "expected_message"),
        [
            ("python", True, "OWASP committees that I found for"),
            ("python", False, "No committees found for"),
            ("", True, "OWASP committees:"),
            ("", False, "No committees found"),
        ],
    )
    @patch("apps.owasp.api.search.committee.get_committees")
    @patch("apps.owasp.models.committee.Committee.active_committees_count")
    def test_committees_blocks_results(
        self,
        mock_active_committees_count,
        mock_get_committees,
        search_query,
        has_results,
        expected_message,
        mock_committee,
    ):
        mock_get_committees.return_value = {"hits": [mock_committee] if has_results else []}
        mock_active_committees_count.return_value = 42

        blocks = committees_blocks(search_query=search_query)

        assert any(expected_message in str(block) for block in blocks)
        if has_results:
            assert any(mock_committee["idx_name"] in str(block) for block in blocks)
