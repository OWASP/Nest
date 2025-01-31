"""Test cases for the algolia_update_suggestions command."""

from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command


class TestUpdateSuggestionsCommand:
    """Test cases for the update_suggestions command."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        """Set up test environment."""
        self.stdout = StringIO()
        with patch(
            "apps.common.management.commands.algolia_update_suggestions.QuerySuggestionsClientSync",
            autospec=True,
        ) as client_patch:
            self.mock_client_class = client_patch
            self.mock_client = client_patch.return_value
            yield

    @pytest.mark.parametrize(
        ("environment", "expected_output"),
        [
            (
                "development",
                "\nThe following query suggestion index were updated:\n"
                "        * Chapters\n"
                "        * Committees\n"
                "        * Issues\n"
                "        * Projects\n"
                "        * Users\n",
            ),
            (
                "production",
                "\nThe following query suggestion index were updated:\n"
                "        * Chapters\n"
                "        * Committees\n"
                "        * Issues\n"
                "        * Projects\n"
                "        * Users\n",
            ),
        ],
    )
    @patch("apps.common.management.commands.algolia_update_suggestions.settings")
    def test_handle_updates(self, mock_settings, environment, expected_output):
        """Test command output with different environments."""
        mock_settings.ENVIRONMENT = environment
        mock_settings.ALGOLIA_APPLICATION_ID = "test_app_id"
        mock_settings.ALGOLIA_WRITE_API_KEY = "test_api_key"
        mock_settings.ALGOLIA_APPLICATION_REGION = "test_region"

        with patch("sys.stdout", new=StringIO()) as fake_out:
            call_command("algolia_update_suggestions")
            assert fake_out.getvalue() == expected_output

    def test_client_configuration(self):
        """Test if client is configured with correct settings."""
        with patch(
            "apps.common.management.commands.algolia_update_suggestions.settings"
        ) as mock_settings:
            mock_settings.ENVIRONMENT = "development"
            mock_settings.ALGOLIA_APPLICATION_ID = "test_app_id"
            mock_settings.ALGOLIA_WRITE_API_KEY = "test_api_key"
            mock_settings.ALGOLIA_APPLICATION_REGION = "test_region"

            call_command("algolia_update_suggestions")

            self.mock_client_class.assert_called_once_with(
                "test_app_id",
                "test_api_key",
                "test_region",
            )

    def test_update_config_calls(self):
        """Test if update_config is called with correct parameters for each entity."""
        with patch(
            "apps.common.management.commands.algolia_update_suggestions.settings"
        ) as mock_settings:
            mock_settings.ENVIRONMENT = "development"

            call_command("algolia_update_suggestions")

            expected_entities = ["chapters", "committees", "issues", "projects", "users"]
            assert self.mock_client.update_config.call_count == len(expected_entities)

            for entity in expected_entities:
                index_name = f"development_{entity}_suggestions"
                source_index_name = f"development_{entity}"

                config_call = next(
                    call
                    for call in self.mock_client.update_config.call_args_list
                    if call[1]["index_name"] == index_name
                )

                config = config_call[1]["configuration"]
                assert "sourceIndices" in config
                assert len(config["sourceIndices"]) == 1
                assert config["sourceIndices"][0]["indexName"] == source_index_name

    @patch("apps.common.management.commands.algolia_update_suggestions.settings")
    def test_entity_configurations(self, mock_settings):
        """Test if entity configurations are properly structured."""
        mock_settings.ENVIRONMENT = "development"

        call_command("algolia_update_suggestions")

        projects_call = next(
            call
            for call in self.mock_client.update_config.call_args_list
            if call[1]["index_name"] == "development_projects_suggestions"
        )

        config = projects_call[1]["configuration"]["sourceIndices"][0]
        assert "facets" in config
        assert "generate" in config

        assert any(facet["attribute"] == "idx_key" for facet in config["facets"])
        assert any(facet["attribute"] == "idx_name" for facet in config["facets"])

        assert ["idx_name"] in config["generate"]
        assert ["idx_tags"] in config["generate"]
