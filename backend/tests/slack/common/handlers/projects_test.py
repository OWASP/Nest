from unittest.mock import patch

import pytest

from apps.slack.common.presentation import EntityPresentation
from apps.slack.handlers.projects import projects_blocks


class TestProjectsHandler:
    @pytest.fixture()
    def mock_project(self):
        return {
            "idx_name": "Test Project",
            "idx_summary": "Test Project Summary",
            "idx_url": "http://example.com/project/1",
            "idx_leaders": ["Leader 1", "Leader 2"],
            "idx_contributors_count": 10,
            "idx_forks_count": 5,
            "idx_stars_count": 100,
            "idx_level": "Flagship",
            "idx_updated_at": "2024-01-01T00:00:00Z",
        }

    @pytest.mark.parametrize(
        ("search_query", "has_results", "expected_message"),
        [
            ("python", True, "OWASP projects that I found for"),
            ("python", False, "No projects found for"),
            ("", True, "OWASP projects:"),
            ("", False, "No projects found"),
        ],
    )
    @patch("apps.owasp.api.search.project.get_projects")
    @patch("apps.owasp.models.project.Project.active_projects_count")
    def test_projects_blocks_results(
        self,
        mock_active_projects_count,
        mock_get_projects,
        search_query,
        has_results,
        expected_message,
        mock_project,
    ):
        mock_get_projects.return_value = {"hits": [mock_project] if has_results else []}
        mock_active_projects_count.return_value = 42

        blocks = projects_blocks(search_query=search_query)

        assert any(expected_message in str(block) for block in blocks)
        if has_results:
            assert any(mock_project["idx_name"] in str(block) for block in blocks)

    @pytest.mark.parametrize(
        ("presentation_params", "expected_content"),
        [
            (
                {"include_metadata": True, "include_timestamps": True},
                ["Contributors: 10", "Updated"],
            ),
            ({"include_metadata": False, "include_timestamps": False}, []),
            ({"name_truncation": 5}, ["Test..."]),
        ],
    )
    @patch("apps.owasp.api.search.project.get_projects")
    def test_projects_blocks_presentation(
        self,
        mock_get_projects,
        presentation_params,
        expected_content,
        mock_project,
    ):
        mock_get_projects.return_value = {"hits": [mock_project]}
        presentation = EntityPresentation(**presentation_params)

        blocks = projects_blocks(presentation=presentation)

        for content in expected_content:
            assert any(content in str(block) for block in blocks)
