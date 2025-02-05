from unittest.mock import MagicMock, mock_open, patch

import pytest
from algoliasearch.http.exceptions import AlgoliaException

from apps.common.index import IndexBase, IndexRegistry

EXPECTED_TOTAL_COUNT = 42


class TestIndexRegistry:
    def test_singleton_instance(self):
        registry1 = IndexRegistry.get_instance()
        registry2 = IndexRegistry.get_instance()
        assert registry1 is registry2

    @patch("os.getenv")
    def test_reload_excluded_patterns(self, mock_getenv):
        mock_getenv.side_effect = lambda key, default="": {
            "ALGOLIA_EXCLUDED_INDICES": "test1,test2,test3",
            "ALGOLIA_EXCLUDED_MODELS": "model1,model2",
        }.get(key, default)

        registry = IndexRegistry.get_instance()
        registry.reload_excluded_patterns()

        assert registry.excluded_patterns == {"test1", "test2", "test3"}
        assert registry.excluded_models == {"model1", "model2"}

    @pytest.mark.parametrize(
        ("name", "check_type", "expected"),
        [
            ("excluded_index", "index", True),
            ("excluded_suggestions", "suggestion", True),
            ("excluded", "model", True),
        ],
    )
    def test_is_excluded(self, name, check_type, expected):
        with patch("os.getenv") as mock_getenv:
            mock_getenv.side_effect = lambda key, default="": {
                "ALGOLIA_EXCLUDED_INDICES": "excluded",
                "ALGOLIA_EXCLUDED_MODELS": "excluded",
            }.get(key, default)

            registry = IndexRegistry.get_instance()
            registry.reload_excluded_patterns()

            assert registry.is_excluded(name, check_type) == expected


class TestIndexBase:
    @pytest.fixture(autouse=True)
    def _setup_mocks(self):
        """Set up test fixtures and mocks."""
        with (
            patch("apps.common.index.settings") as self.mock_settings,
            patch("apps.common.index.logger") as self.mock_logger,
            patch("apps.common.index.SearchClientSync") as self.mock_search_client,
        ):
            self.mock_settings.ENVIRONMENT = "testenv"
            self.mock_settings.ALGOLIA_APPLICATION_ID = "test_app_id"
            self.mock_settings.ALGOLIA_WRITE_API_KEY = "test_api_key"
            self.mock_client = MagicMock()
            self.mock_search_client.return_value = self.mock_client
            yield

    def test_reindex_synonyms(self):
        file_content = "term: syn1, syn2"

        with patch("pathlib.Path.open", mock_open(read_data=file_content)):
            result = IndexBase.reindex_synonyms("test_app", "test_index")

            self.mock_client.clear_synonyms.assert_called_once()
            self.mock_client.save_synonyms.assert_called_once()
            assert result == 1

    def test_reindex_synonyms_error(self):
        file_content = "term: syn1, syn2"
        self.mock_client.save_synonyms.side_effect = AlgoliaException("Error")

        with patch("pathlib.Path.open", mock_open(read_data=file_content)):
            result = IndexBase.reindex_synonyms("test_app", "test_index")
            assert result is None

    def test_get_total_count(self):
        self.mock_client.search_single_index.return_value = MagicMock(nb_hits=EXPECTED_TOTAL_COUNT)
        IndexBase.get_total_count.cache_clear()

        result = IndexBase.get_total_count("test_index")
        assert result == EXPECTED_TOTAL_COUNT

    def test_get_total_count_error(self):
        self.mock_client.search_single_index.side_effect = AlgoliaException("Error")
        IndexBase.get_total_count.cache_clear()

        result = IndexBase.get_total_count("test_index")
        assert result == 0
