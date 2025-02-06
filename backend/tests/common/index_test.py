from unittest.mock import MagicMock, mock_open, patch

import pytest
from algoliasearch.http.exceptions import AlgoliaException
from algoliasearch_django import AlgoliaIndex

from apps.common.index import IndexBase, IndexRegistry, conditional_register, should_create_index

TOTAL_COUNT = 42


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

    @patch("os.getenv")
    def test_reload_excluded_patterns_empty(self, mock_getenv):
        mock_getenv.return_value = ""
        registry = IndexRegistry.get_instance()
        registry.reload_excluded_patterns()

        assert registry.excluded_patterns == set()
        assert registry.excluded_models == set()

    @pytest.mark.parametrize(
        ("name", "check_type", "excluded_indices", "expected"),
        [
            ("excluded_index", "index", "excluded", True),
            ("not_excluded", "index", "other_pattern", False),
            ("test_base", "suggestion", "test", True),
            ("other_suggestions", "suggestion", "test", False),
            ("excluded", "model", "excluded", True),
        ],
    )
    def test_is_excluded(self, name, check_type, excluded_indices, expected):
        with patch("os.getenv") as mock_getenv:
            mock_getenv.side_effect = lambda key, default="": {
                "ALGOLIA_EXCLUDED_INDICES": excluded_indices,
                "ALGOLIA_EXCLUDED_MODELS": "excluded",
            }.get(key, default)

            registry = IndexRegistry.get_instance()
            registry.reload_excluded_patterns()

            assert registry.is_excluded(name, check_type) == expected


class TestShouldCreateIndex:
    @pytest.mark.parametrize(
        ("is_local", "index_name", "index_type", "excluded_indices", "expected"),
        [
            (False, "any_index", "index", "excluded", True),
            (True, "not_excluded", "index", "other_pattern", True),
            (True, "excluded_index", "index", "excluded", False),
            (True, "test_base_suggestions", "suggestion", "test", False),
            (True, "other_suggestions", "suggestion", "excluded", True),
        ],
    )
    def test_should_create_index(
        self, is_local, index_name, index_type, excluded_indices, expected
    ):
        with (
            patch("apps.common.index.IS_LOCAL_BUILD", is_local),
            patch("os.getenv") as mock_getenv,
        ):
            mock_getenv.side_effect = lambda key, default="": {
                "ALGOLIA_EXCLUDED_INDICES": excluded_indices,
            }.get(key, default)

            registry = IndexRegistry.get_instance()
            registry.reload_excluded_patterns()

            assert should_create_index(index_name, index_type) == expected


class MockAlgoliaRegister:
    def __init__(self, model, **kwargs):
        self.model = model
        self.kwargs = kwargs

    def __call__(self, cls):
        return cls


@patch("apps.common.index.algolia_register", MockAlgoliaRegister)
class TestConditionalRegister:
    @pytest.fixture()
    def mock_model(self):
        model = MagicMock()
        model._meta.app_label = "test_app"
        model._meta.model_name = "test_model"
        return model

    @patch("apps.common.index.settings")
    @patch("apps.common.index.should_create_index")
    def test_conditional_register_included(self, mock_should_create, mock_settings, mock_model):
        mock_should_create.return_value = True
        mock_settings.ENVIRONMENT = "test"

        class TestIndex(AlgoliaIndex):
            index_name = "test_index"

        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = ""

            decorated = conditional_register(mock_model)(TestIndex)
            assert isinstance(decorated, type)
            assert issubclass(decorated, AlgoliaIndex)

    @patch("apps.common.index.settings")
    @patch("apps.common.index.should_create_index")
    def test_conditional_register_excluded(self, mock_should_create, mock_settings, mock_model):
        mock_should_create.return_value = False
        mock_settings.ENVIRONMENT = "test"

        class TestIndex(AlgoliaIndex):
            index_name = "test_index"

        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = "test_app/test_model"

            decorated = conditional_register(mock_model)(TestIndex)
            assert decorated is TestIndex


class TestIndexBase:
    @pytest.fixture(autouse=True)
    def _setup(self):
        with (
            patch("apps.common.index.settings") as self.mock_settings,
            patch("apps.common.index.SearchClientSync") as self.mock_search_client,
            patch("apps.common.index.QuerySuggestionsClientSync") as self.mock_suggestions_client,
            patch("apps.common.index.logger") as self.mock_logger,
        ):
            self.mock_settings.ENVIRONMENT = "test"
            self.mock_settings.ALGOLIA_APPLICATION_ID = "test_id"
            self.mock_settings.ALGOLIA_WRITE_API_KEY = "test_key"
            self.mock_settings.BASE_DIR = "/test/base/dir"
            self.mock_client = MagicMock()
            self.mock_search_client.return_value = self.mock_client
            yield

    @pytest.mark.parametrize(
        ("is_local", "should_create", "expected_replicas"),
        [
            (False, True, ["replica1", "replica2"]),
            (True, True, ["replica1"]),
            (True, False, []),
        ],
    )
    def test_configure_replicas(self, is_local, should_create, expected_replicas):
        replicas = {"replica1": ["custom"], "replica2": ["asc"]}
        base_index_name = "test_base_index"

        with (
            patch("apps.common.index.IS_LOCAL_BUILD", is_local),
            patch("apps.common.index.should_create_index") as mock_should_create,
        ):

            def mock_should_create_func(name, _type="index"):
                if name == f"test_{base_index_name}":
                    return should_create
                if is_local:
                    return name == "replica1"
                return True

            mock_should_create.side_effect = mock_should_create_func

            IndexBase.configure_replicas("test", base_index_name, replicas)

            if should_create:
                self.mock_client.set_settings.assert_any_call(
                    f"test_{base_index_name}", {"replicas": expected_replicas}
                )

    def test_parse_synonyms_file_empty(self):
        with patch("pathlib.Path.open", mock_open(read_data="\n  \n# comment\n")):
            result = IndexBase._parse_synonyms_file("test.txt")
            assert result == []

    def test_get_total_count_error(self):
        index_name = "test_index"

        with (
            patch("apps.common.index.settings") as mock_settings,
            patch("apps.common.index.logger") as mock_logger,
            patch("apps.common.index.SearchClientSync") as mock_search_client,
        ):
            mock_settings.ENVIRONMENT = "testenv"
            mock_settings.ALGOLIA_APPLICATION_ID = "test_app_id"
            mock_settings.ALGOLIA_WRITE_API_KEY = "test_api_key"

            mock_client = MagicMock()
            mock_client.search_single_index.side_effect = AlgoliaException("API Error")
            mock_search_client.return_value = mock_client

            IndexBase.get_total_count.cache_clear()

            result = IndexBase.get_total_count(index_name)

            assert result == 0
            mock_logger.exception.assert_called_once_with(
                "Error retrieving index count for '%s'", index_name
            )
            mock_client.search_single_index.assert_called_once_with(
                index_name="testenv_test_index",
                search_params={"query": "", "hitsPerPage": 0, "analytics": False},
            )

    def test_get_total_count_cache(self):
        mock_response = MagicMock()
        mock_response.nb_hits = 42
        self.mock_client.search_single_index.return_value = mock_response

        IndexBase.get_total_count.cache_clear()
        result1 = IndexBase.get_total_count("test_index")
        result2 = IndexBase.get_total_count("test_index")

        assert result1 == result2 == TOTAL_COUNT
        self.mock_client.search_single_index.assert_called_once()
