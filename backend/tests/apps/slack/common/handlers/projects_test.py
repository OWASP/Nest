from unittest.mock import patch

import pytest

from apps.slack.common.handlers.projects import get_blocks
from apps.slack.common.presentation import EntityPresentation


class TestProjectHandler:
    @pytest.fixture
    def mock_project_data(self):
        return {
            "hits": [
                {
                    "idx_name": "Test Project",
                    "idx_contributors_count": 10,
                    "idx_forks_count": 5,
                    "idx_stars_count": 100,
                    "idx_leaders": ["John Doe", "Jane Smith"],
                    "idx_summary": "This is a test project summary",
                    "idx_url": "https://example.com/project",
                    "idx_updated_at": "1704067200",  # 2024-01-01
                    "idx_level": "Flagship",
                }
            ],
            "nbPages": 2,
        }

    @pytest.fixture
    def mock_empty_project_data(self):
        return {
            "hits": [],
            "nbPages": 0,
        }

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        with (
            patch("apps.owasp.api.search.project.get_projects") as mock_get_projects,
            patch("apps.owasp.models.project.Project") as mock_project_model,
        ):
            mock_project_model.active_projects_count.return_value = 42
            yield {"get_projects": mock_get_projects, "project_model": mock_project_model}

    def test_get_blocks_with_results(self, setup_mocks, mock_project_data):
        setup_mocks["get_projects"].return_value = mock_project_data

        blocks = get_blocks(search_query="test")

        assert "OWASP projects that I found for" in blocks[0]["text"]["text"]
        assert "Test Project" in blocks[1]["text"]["text"]
        assert "Contributors: 10" in blocks[1]["text"]["text"]
        assert "Forks: 5" in blocks[1]["text"]["text"]
        assert "Stars: 100" in blocks[1]["text"]["text"]
        assert "Leaders: John Doe, Jane Smith" in blocks[1]["text"]["text"]

    def test_get_blocks_no_results(self, setup_mocks, mock_empty_project_data):
        setup_mocks["get_projects"].return_value = mock_empty_project_data

        blocks = get_blocks(search_query="nonexistent")

        assert len(blocks) == 1
        assert "No projects found for" in blocks[0]["text"]["text"]

    def test_get_blocks_text_truncation(self, setup_mocks):
        long_name = "Very Long Project Name That Should Be Truncated"
        mock_data = {
            "hits": [
                {
                    "idx_name": long_name,
                    "idx_summary": "Test Summary",
                    "idx_url": "https://example.com",
                    "idx_updated_at": "1704067200",
                    "idx_contributors_count": 10,
                    "idx_forks_count": 5,
                    "idx_stars_count": 100,
                    "idx_leaders": ["John Doe", "Jane Smith"],
                    "idx_level": "Flagship",
                }
            ],
            "nbPages": 1,
        }
        setup_mocks["get_projects"].return_value = mock_data

        presentation = EntityPresentation(name_truncation=20)
        blocks = get_blocks(presentation=presentation)

        assert long_name[:17] + "..." in blocks[1]["text"]["text"]

    def test_get_blocks_with_timestamps(self, setup_mocks, mock_project_data):
        setup_mocks["get_projects"].return_value = mock_project_data
        presentation = EntityPresentation(include_timestamps=True)

        blocks = get_blocks(presentation=presentation)

        assert "Updated" in blocks[1]["text"]["text"]

    def test_feedback_message(self, setup_mocks, mock_project_data):
        setup_mocks["get_projects"].return_value = mock_project_data
        presentation = EntityPresentation(include_feedback=True)

        blocks = get_blocks(presentation=presentation)

        assert "Extended search over 42 OWASP projects" in blocks[-1]["text"]["text"]

    def test_search_query_escaping(self, setup_mocks, mock_project_data):
        setup_mocks["get_projects"].return_value = mock_project_data
        dangerous_query = "test & <script>"

        blocks = get_blocks(search_query=dangerous_query)

        assert "&amp;" in blocks[0]["text"]["text"]
        assert "&lt;script&gt;" in blocks[0]["text"]["text"]

    def test_pagination(self, setup_mocks, mock_project_data):
        mock_project_data["nbPages"] = 3
        setup_mocks["get_projects"].return_value = mock_project_data
        presentation = EntityPresentation(include_pagination=True)

        with patch(
            "apps.slack.common.handlers.projects.get_pagination_buttons"
        ) as mock_pagination:
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
            element_count = 2
            page_no = 2
            blocks = get_blocks(page=page_no, presentation=presentation)
            assert len(blocks[-1]["elements"]) == element_count
            assert mock_pagination.call_count == element_count

    def test_no_pagination_when_disabled(self, setup_mocks, mock_project_data):
        mock_project_data["nbPages"] = 3
        setup_mocks["get_projects"].return_value = mock_project_data
        presentation = EntityPresentation(include_pagination=False)

        blocks = get_blocks(presentation=presentation)
        assert blocks[-1]["type"] != "actions"

    def test_various_metadata_combinations(self, setup_mocks):
        test_cases = [
            {"idx_contributors_count": 0, "idx_forks_count": 0, "idx_stars_count": 0},
            {"idx_contributors_count": 10, "idx_forks_count": 0, "idx_stars_count": 0},
            {"idx_contributors_count": 0, "idx_forks_count": 5, "idx_stars_count": 0},
            {"idx_contributors_count": 0, "idx_forks_count": 0, "idx_stars_count": 100},
            {"idx_contributors_count": 10, "idx_forks_count": 5, "idx_stars_count": 0},
        ]

        for case in test_cases:
            mock_data = {
                "hits": [
                    {
                        "idx_name": "Test Project",
                        "idx_summary": "Summary",
                        "idx_url": "https://example.com",
                        "idx_updated_at": "1704067200",
                        "idx_leaders": ["Leader"],
                        "idx_level": "Flagship",
                        **case,
                    }
                ],
                "nbPages": 1,
            }
            setup_mocks["get_projects"].return_value = mock_data

            presentation = EntityPresentation(include_timestamps=False)
            blocks = get_blocks(presentation=presentation)

            if all(v == 0 for v in case.values()):
                metadata_text = "_" in blocks[1]["text"]["text"]
                assert not metadata_text or "Leaders" in blocks[1]["text"]["text"]

            for field, value in case.items():
                field_name = field.replace("idx_", "").replace("_count", "").title()
                if value > 0:
                    assert f"{field_name}: {value}" in blocks[1]["text"]["text"]
                else:
                    assert f"{field_name}: {value}" not in blocks[1]["text"]["text"]

    def test_empty_leaders(self, setup_mocks):
        mock_data = {
            "hits": [
                {
                    "idx_name": "Test Project",
                    "idx_summary": "Summary",
                    "idx_url": "https://example.com",
                    "idx_updated_at": "1704067200",
                    "idx_contributors_count": 10,
                    "idx_forks_count": 5,
                    "idx_stars_count": 100,
                    "idx_leaders": [],
                    "idx_level": "Flagship",
                }
            ],
            "nbPages": 1,
        }
        setup_mocks["get_projects"].return_value = mock_data

        blocks = get_blocks()
        assert "Leaders:" not in blocks[1]["text"]["text"]

    def test_pagination_empty(self, setup_mocks, mock_project_data):
        mock_project_data["nbPages"] = 1
        setup_mocks["get_projects"].return_value = mock_project_data
        presentation = EntityPresentation(include_pagination=True)

        with patch("apps.slack.common.handlers.projects.get_pagination_buttons", return_value=[]):
            blocks = get_blocks(page=1, presentation=presentation)
            assert all(block["type"] != "actions" for block in blocks)

    def test_feedback_with_search_query(self, setup_mocks, mock_project_data):
        setup_mocks["get_projects"].return_value = mock_project_data
        search_query = "test query"
        presentation = EntityPresentation(include_feedback=True)

        blocks = get_blocks(search_query=search_query, presentation=presentation)

        feedback_block = blocks[-1]["text"]["text"]
        assert "Extended search over 42 OWASP projects" in feedback_block
        assert f"?q={search_query}" in feedback_block

    def test_pagination_edge_case(self, setup_mocks, mock_project_data):
        mock_project_data["nbPages"] = 2
        setup_mocks["get_projects"].return_value = mock_project_data
        presentation = EntityPresentation(include_pagination=True)

        expected_element_count = 2

        with patch(
            "apps.slack.common.handlers.projects.get_pagination_buttons"
        ) as mock_pagination:
            mock_pagination.return_value = None
            blocks = get_blocks(page=2, presentation=presentation)
            assert all(block["type"] != "actions" for block in blocks)
            assert mock_pagination.called
            assert len(blocks[-1]["elements"]) == expected_element_count
            assert mock_pagination.call_count == expected_element_count

    def test_leaders_metadata_disabled(self, setup_mocks, mock_project_data):
        setup_mocks["get_projects"].return_value = mock_project_data
        presentation = EntityPresentation(include_metadata=False)

        blocks = get_blocks(presentation=presentation)

        assert "Leaders:" not in blocks[1]["text"]["text"]
