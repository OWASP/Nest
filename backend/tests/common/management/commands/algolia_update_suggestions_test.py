from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command

UPDATE_CONFIG_CALLS_COUNT = 5


class TestUpdateSuggestionsCommand:
    @pytest.fixture(autouse=True)
    def _setup(self):
        """Set up test fixtures."""
        self.stdout = StringIO()
        with patch(
            "apps.common.management.commands.algolia_update_suggestions.IndexBase.get_suggestions_client",
            autospec=True,
        ) as client_patch:
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
    def test_handle_updates(self, environment, expected_output):
        with (
            patch(
                "apps.common.management.commands.algolia_update_suggestions.settings"
            ) as mock_settings,
            patch("apps.common.index.is_indexable", return_value=True),
            patch("sys.stdout", new=StringIO()) as fake_out,
        ):
            mock_settings.ENVIRONMENT = environment
            call_command("algolia_update_suggestions")
            assert fake_out.getvalue() == expected_output

    def test_skips_excluded_suggestions(self):
        with (
            patch(
                "apps.common.management.commands.algolia_update_suggestions.settings"
            ) as mock_settings,
            patch("apps.common.index.is_indexable") as mock_is_indexable,
            patch("sys.stdout", new=StringIO()) as fake_out,
        ):
            mock_settings.ENVIRONMENT = "development"

            def mock_side_effect(name, index_type):
                return name == "development_chapters_suggestions" and index_type == "suggestion"

            mock_is_indexable.side_effect = mock_side_effect

            call_command("algolia_update_suggestions")
            output = fake_out.getvalue()

            assert "\nThe following query suggestion index were updated:" in output
            assert "* Chapters" in output

            assert self.mock_client.update_config.call_count == UPDATE_CONFIG_CALLS_COUNT

            update_call = self.mock_client.update_config.call_args_list[0]
            assert update_call[1]["index_name"] == "development_chapters_suggestions"

    def test_entity_configurations(self):
        with (
            patch(
                "apps.common.management.commands.algolia_update_suggestions.settings"
            ) as mock_settings,
            patch("apps.common.index.is_indexable", return_value=True),
        ):
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
