from unittest.mock import MagicMock, mock_open, patch

import pytest
from algoliasearch.http.exceptions import AlgoliaException
from algoliasearch_django import AlgoliaIndex
from django.conf import settings
from django.test import override_settings

from apps.common.index import (
    EXCLUDED_LOCAL_INDEX_NAMES,
    IndexBase,
    IndexRegistry,
    is_indexable,
    register,
)

ENV = settings.ENVIRONMENT.lower()
TOTAL_COUNT = 42


class TestIndexRegistry:
    def test_singleton_instance(self):
        registry1 = IndexRegistry.get_instance()
        registry2 = IndexRegistry.get_instance()
        assert registry1 is registry2

    @pytest.mark.parametrize(
        ("excluded_index_names", "expected"),
        [
            ("test1,test2,test3", {"test1", "test2", "test3"}),
            ("test1, test2, test3", {"test1", "test2", "test3"}),
            ("", set(EXCLUDED_LOCAL_INDEX_NAMES)),
            (None, set(EXCLUDED_LOCAL_INDEX_NAMES)),
        ],
    )
    def test_load_excluded_index_names(self, excluded_index_names, expected):
        with override_settings(ALGOLIA_EXCLUDED_LOCAL_INDEX_NAMES=excluded_index_names):
            registry = IndexRegistry.get_instance().load_excluded_local_index_names()

        assert registry.excluded_local_index_names == expected

    @pytest.mark.parametrize(
        ("is_local", "index_name", "excluded_index_names", "expected"),
        [
            (False, "excluded", "excluded", True),
            (True, "other_name", "excluded_name", True),
            (True, "excluded_index", "excluded_index", False),
        ],
    )
    def test_is_indexable(self, is_local, index_name, excluded_index_names, expected):
        with (
            patch("apps.common.index.IS_LOCAL_BUILD", is_local),
            override_settings(ALGOLIA_EXCLUDED_LOCAL_INDEX_NAMES=excluded_index_names),
        ):
            IndexRegistry.get_instance().load_excluded_local_index_names()

            assert is_indexable(index_name) == expected


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
    @patch("apps.common.index.is_indexable")
    def test_conditional_register_included(self, mock_is_indexable, mock_settings, mock_model):
        mock_is_indexable.return_value = True
        mock_settings.ENVIRONMENT = "test"

        class TestIndex(AlgoliaIndex):
            index_name = "test_index"

        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = ""

            decorated = register(mock_model)(TestIndex)
            assert isinstance(decorated, type)
            assert issubclass(decorated, AlgoliaIndex)

    @patch("apps.common.index.settings")
    @patch("apps.common.index.is_indexable")
    def test_conditional_register_excluded(self, mock_is_indexable, mock_settings, mock_model):
        mock_is_indexable.return_value = False
        mock_settings.ENVIRONMENT = "test"

        class TestIndex(AlgoliaIndex):
            index_name = "test_index"

        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = "test_app/test_model"

            decorated = register(mock_model)(TestIndex)
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
        ("is_local", "is_indexable", "expected_replicas"),
        [
            (
                False,
                True,
                ["test_index_name_index_name_attr_asc", "test_index_name_index_name_attr_desc"],
            ),
            (True, True, ["test_index_name_index_name_attr_asc"]),
            (True, False, []),
        ],
    )
    def test_configure_replicas(self, is_local, is_indexable, expected_replicas):
        replicas = {"index_name_attr_asc": ["asc"], "index_name_attr_desc": ["desc"]}
        index_name = "index_name"

        with (
            patch("apps.common.index.IS_LOCAL_BUILD", is_local),
            patch("apps.common.index.is_indexable") as mock_is_indexable,
        ):

            def mock_is_indexable_func(name):
                if name == index_name:
                    return is_indexable
                if is_local:
                    return name in {"index_name_index_name_attr_asc"}
                return True

            mock_is_indexable.side_effect = mock_is_indexable_func

            IndexBase.configure_replicas(index_name, replicas)

            if is_indexable:
                self.mock_client.set_settings.assert_any_call(
                    f"{ENV}_{index_name}", {"replicas": expected_replicas}
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
        mock_response.nb_hits = TOTAL_COUNT
        self.mock_client.search_single_index.return_value = mock_response

        IndexBase.get_total_count.cache_clear()
        result1 = IndexBase.get_total_count("test_index")
        result2 = IndexBase.get_total_count("test_index")

        assert result1 == result2 == TOTAL_COUNT
        self.mock_client.search_single_index.assert_called_once()
