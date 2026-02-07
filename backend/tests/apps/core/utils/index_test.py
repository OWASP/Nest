"""Tests for core index utilities."""

from unittest.mock import MagicMock, patch

from apps.core.utils.index import (
    DisableIndexing,
    clear_index_cache,
    deep_camelize,
    get_params_for_index,
)


class TestDisableIndexing:
    """Test the DisableIndexing context manager."""

    @patch("apps.core.utils.index.DisableIndexing.unregister_indexes")
    @patch("apps.core.utils.index.DisableIndexing.register_indexes")
    def test_disable_indexing_context_manager(self, mock_register, mock_unregister):
        """Test that the context manager properly disables and re-enables indexing."""
        with DisableIndexing():
            mock_unregister.assert_called_once()
            mock_register.assert_not_called()

        mock_register.assert_called_once()

    @patch("apps.core.utils.index.DisableIndexing.unregister_indexes")
    @patch("apps.core.utils.index.DisableIndexing.register_indexes")
    @patch("django.apps.apps.get_app_config")
    def test_disable_indexing_with_custom_app_names(
        self, mock_get_app_config, mock_register, mock_unregister
    ):
        """Test that the context manager works with custom app names."""
        custom_apps = ("custom_app", "another_app")

        mock_app_config = MagicMock()
        mock_app_config.get_models.return_value = []
        mock_get_app_config.return_value = mock_app_config

        with DisableIndexing(custom_apps):
            mock_unregister.assert_called_once()
            mock_register.assert_not_called()

        mock_register.assert_called_once()


class TestDeepCamelize:
    """Test the deep_camelize function."""

    def test_deep_camelize_empty_input(self):
        """Test that empty/None input returns as-is."""
        assert deep_camelize(None) is None
        assert deep_camelize({}) == {}
        assert deep_camelize([]) == []

    def test_deep_camelize_dict(self):
        """Test dictionary key conversion."""
        input_dict = {"snake_case": "value", "idx_another_key": "another"}
        result = deep_camelize(input_dict)

        assert "snakeCase" in result
        assert "anotherKey" in result
        assert result["snakeCase"] == "value"

    def test_deep_camelize_nested_dict(self):
        """Test nested dictionary conversion."""
        input_dict = {
            "outer_key": {
                "inner_key": "value",
            }
        }
        result = deep_camelize(input_dict)

        assert "outerKey" in result
        assert "innerKey" in result["outerKey"]

    def test_deep_camelize_list(self):
        """Test list of dictionaries conversion."""
        input_list = [
            {"first_item": 1},
            {"second_item": 2},
        ]
        result = deep_camelize(input_list)

        assert len(result) == 2
        assert "firstItem" in result[0]
        assert "secondItem" in result[1]

    def test_deep_camelize_non_dict_non_list(self):
        """Test that non-dict/list values are returned as-is."""
        assert deep_camelize("string") == "string"
        assert deep_camelize(123) == 123


class TestGetParamsForIndex:
    """Test the get_params_for_index function."""

    def test_get_params_for_issues(self):
        """Test parameters for issues index."""
        params = get_params_for_index("issues")

        assert "attributesToRetrieve" in params
        assert "idx_comments_count" in params["attributesToRetrieve"]
        assert "idx_title" in params["attributesToRetrieve"]
        assert params["distinct"] == 1

    def test_get_params_for_chapters(self):
        """Test parameters for chapters index."""
        params = get_params_for_index("chapters")

        assert "attributesToRetrieve" in params
        assert "_geoloc" in params["attributesToRetrieve"]
        assert "idx_region" in params["attributesToRetrieve"]
        assert params["aroundLatLngViaIP"]

    def test_get_params_for_programs(self):
        """Test parameters for programs index."""
        params = get_params_for_index("programs")

        assert "attributesToRetrieve" in params
        assert "idx_name" in params["attributesToRetrieve"]
        assert "idx_status" in params["attributesToRetrieve"]

    def test_get_params_for_projects(self):
        """Test parameters for projects index."""
        params = get_params_for_index("projects")

        assert "attributesToRetrieve" in params
        assert "idx_level" in params["attributesToRetrieve"]
        assert "idx_languages" in params["attributesToRetrieve"]

    def test_get_params_for_committees(self):
        """Test parameters for committees index."""
        params = get_params_for_index("committees")

        assert "attributesToRetrieve" in params
        assert "idx_leaders" in params["attributesToRetrieve"]

    def test_get_params_for_users(self):
        """Test parameters for users index."""
        params = get_params_for_index("users")

        assert "attributesToRetrieve" in params
        assert "idx_login" in params["attributesToRetrieve"]
        assert "idx_avatar_url" in params["attributesToRetrieve"]

    def test_get_params_for_organizations(self):
        """Test parameters for organizations index."""
        params = get_params_for_index("organizations")

        assert "attributesToRetrieve" in params
        assert "idx_location" in params["attributesToRetrieve"]

    def test_get_params_for_unknown_index(self):
        """Test parameters for unknown index returns empty list."""
        params = get_params_for_index("unknown_index")

        assert params["attributesToRetrieve"] == []

    def test_common_params_always_present(self):
        """Test that common params are always present."""
        for index in ["issues", "chapters", "projects", "unknown"]:
            params = get_params_for_index(index)
            assert "attributesToHighlight" in params
            assert "removeWordsIfNoResults" in params
            assert "minProximity" in params
            assert "typoTolerance" in params


class TestClearIndexCache:
    """Test the clear_index_cache function."""

    @patch("apps.core.utils.index.cache")
    @patch("apps.core.utils.index.logger")
    def test_clear_index_cache_no_index_name(self, mock_logger, mock_cache):
        """Test that empty index name does nothing."""
        clear_index_cache("")

        mock_logger.info.assert_called_with("No index name provided, skipping cache clear.")
        mock_cache.iter_keys.assert_not_called()

    @patch("apps.core.utils.index.cache")
    @patch("apps.core.utils.index.logger")
    def test_clear_index_cache_no_matching_keys(self, mock_logger, mock_cache):
        """Test when no matching keys are found."""
        mock_cache.iter_keys.return_value = iter([])

        clear_index_cache("projects")

        mock_logger.info.assert_called()
        mock_cache.delete.assert_not_called()

    @patch("apps.core.utils.index.cache")
    @patch("apps.core.utils.index.logger")
    def test_clear_index_cache_with_matching_keys(self, mock_logger, mock_cache):
        """Test that matching keys are deleted."""
        mock_cache.iter_keys.return_value = iter(["algolia:projects:1", "algolia:projects:2"])

        clear_index_cache("projects")

        assert mock_cache.delete.call_count == 2
