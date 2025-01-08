from unittest.mock import MagicMock, patch

import pytest

from apps.common.management.commands.algolia_update_suggestions import Command

EXPECTED_CALL_COUNT = 4


class TestUpdateSuggestionsCommand:
    @pytest.mark.parametrize(
        ("entity", "facets", "generate"),
        [
            (
                "chapters",
                [
                    {"attribute": "idx_key"},
                    {"attribute": "idx_name"},
                    {"attribute": "idx_tags"},
                    {"attribute": "idx_country"},
                    {"attribute": "idx_region"},
                    {"attribute": "idx_suggested_location"},
                ],
                [
                    ["idx_name"],
                    ["idx_tags"],
                    ["idx_country"],
                    ["idx_region"],
                    ["idx_suggested_location"],
                ],
            ),
            (
                "committees",
                [
                    {"attribute": "idx_key"},
                    {"attribute": "idx_name"},
                    {"attribute": "idx_tags"},
                ],
                [
                    ["idx_name"],
                    ["idx_tags"],
                ],
            ),
            (
                "issues",
                [
                    {"attribute": "idx_title"},
                    {"attribute": "idx_project_name"},
                    {"attribute": "idx_repository_name"},
                    {"attribute": "idx_project_tags"},
                    {"attribute": "idx_repository_topics"},
                ],
                [
                    ["idx_title"],
                    ["idx_project_name"],
                    ["idx_repository_name"],
                    ["idx_project_tags"],
                    ["idx_repository_topics"],
                ],
            ),
            (
                "projects",
                [
                    {"attribute": "idx_key"},
                    {"attribute": "idx_name"},
                    {"attribute": "idx_repository_names"},
                    {"attribute": "idx_tags"},
                ],
                [
                    ["idx_name"],
                    ["idx_tags"],
                    ["idx_repository_names"],
                ],
            ),
        ],
    )
    @patch("apps.common.management.commands.algolia_update_suggestions.settings")
    @patch("apps.common.management.commands.algolia_update_suggestions.QuerySuggestionsClientSync")
    def test_handle(self, mock_query_suggestions_client, mock_settings, entity, facets, generate):
        # mocks
        mock_settings.ENVIRONMENT = "testenv"
        mock_settings.ALGOLIA_APPLICATION_ID = "mock_app_id"
        mock_settings.ALGOLIA_WRITE_API_KEY = "mock_api_key"
        mock_settings.ALGOLIA_APPLICATION_REGION = "eu"

        mock_client = MagicMock()
        mock_query_suggestions_client.return_value = mock_client

        mock_client.update_config.return_value = None

        # Act
        command = Command()
        command.handle()

        mock_query_suggestions_client.assert_called_once_with("mock_app_id", "mock_api_key", "eu")

        mock_client.update_config.assert_any_call(
            index_name=f"testenv_{entity}_suggestions",
            configuration={
                "sourceIndices": [
                    {
                        "indexName": f"testenv_{entity}",
                        "facets": facets,
                        "generate": generate,
                    }
                ]
            },
        )

        # Use constant for the expected call count
        assert mock_client.update_config.call_count == EXPECTED_CALL_COUNT
