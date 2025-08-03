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
            patch("apps.owasp.index.search.project.get_projects") as mock_get_projects,
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
