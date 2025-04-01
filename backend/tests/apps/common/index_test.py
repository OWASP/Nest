from pathlib import Path
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
EXPECTED_SYNONYMS_COUNT = 3
EXPECTED_REINDEX_RESULT = 2


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
    @pytest.fixture
    def mock_model(self):
        model = MagicMock()
        model._meta.app_label = "test_app"
        model._meta.model_name = "test_model"
        return model

    @pytest.fixture()
    def _mock_db_settings(self):
        """Mock database settings to prevent connection errors during tests."""
        with patch.dict(
            "os.environ",
            {
                "DJANGO_DB_HOST": "localhost",
                "DJANGO_DB_NAME": "test_db",
                "DJANGO_DB_PASSWORD": "test_password",
                "DJANGO_DB_USER": "test_user",
                "DJANGO_DB_PORT": "5432",
            },
        ):
            yield

    @pytest.mark.usefixtures("_mock_db_settings")
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

    @pytest.mark.usefixtures("_mock_db_settings")
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

    @patch("apps.common.index.settings")
    @patch("apps.common.index.is_indexable")
    def test_conditional_register_with_db_env_vars(
        self, mock_is_indexable, mock_settings, mock_model
    ):
        """Test registration with explicit database environment variables."""
        mock_is_indexable.return_value = True
        mock_settings.ENVIRONMENT = "test"

        class TestIndex(AlgoliaIndex):
            index_name = "test_index"

        with patch.dict(
            "os.environ",
            {
                "DJANGO_DB_HOST": "test-db-host",
                "DJANGO_DB_NAME": "test-db-name",
                "DJANGO_DB_PASSWORD": "test-db-password",
                "DJANGO_DB_USER": "test-db-user",
                "DJANGO_DB_PORT": "5432",
            },
        ), patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = ""

            decorated = register(mock_model)(TestIndex)
            assert isinstance(decorated, type)
            assert issubclass(decorated, AlgoliaIndex)


class TestIndexBase:
    @pytest.fixture(autouse=True)
    def _setup(self):
        with (
            patch("apps.common.index.settings") as self.mock_settings,
            patch("apps.common.index.SearchClientSync") as self.mock_search_client,
            patch("apps.common.index.logger") as self.mock_logger,
        ):
            self.mock_settings.ENVIRONMENT = "test"
            self.mock_settings.ALGOLIA_APPLICATION_ID = "test_id"
            self.mock_settings.ALGOLIA_WRITE_API_KEY = "test_key"
            self.mock_settings.BASE_DIR = "/test/base/dir"
            self.mock_client = MagicMock()
            self.mock_search_client.return_value = self.mock_client
            yield

    def test_get_client_with_ip_address(self):
        """Test get_client with IP address."""
        with patch("apps.common.index.SearchConfig") as mock_search_config:
            mock_config = MagicMock()
            mock_search_config.return_value = mock_config

            IndexBase.get_client(ip_address="192.168.1.1")

            mock_search_config.assert_called_once_with("test_id", "test_key")

            mock_config.headers.__setitem__.assert_called_once_with(
                "X-Forwarded-For", "192.168.1.1"
            )

            self.mock_search_client.assert_called_once_with(config=mock_config)

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

    def test_configure_replicas_not_indexable(self):
        """Test configure_replicas when index name is not indexable."""
        index_name = "not_indexable_index"
        replicas = {"attr_asc": ["asc"]}

        with patch("apps.common.index.is_indexable", return_value=False):
            result = IndexBase.configure_replicas(index_name, replicas)

            assert result is None
            self.mock_client.set_settings.assert_not_called()

    def test_parse_synonyms_file_empty(self):
        with patch("pathlib.Path.open", mock_open(read_data="\n  \n")):
            result = IndexBase._parse_synonyms_file("test.txt")
            assert result == []

    def test_parse_synonyms_file(self):
        """Test _parse_synonyms_file method."""
        mock_file_content = """

        brave, courageous


        cat: kitten, kitty


        dog: puppy, pup
        """

        with patch("pathlib.Path.open", mock_open(read_data=mock_file_content)):
            result = IndexBase._parse_synonyms_file("test.txt")

        assert len(result) == EXPECTED_SYNONYMS_COUNT

        assert result[0]["type"] == "synonym"
        assert "brave" in result[0]["synonyms"]
        assert "courageous" in result[0]["synonyms"]

        assert result[1]["type"] == "oneWaySynonym"
        assert result[1]["input"] == "cat"
        assert "kitten" in result[1]["synonyms"]
        assert "kitty" in result[1]["synonyms"]

        assert result[2]["type"] == "oneWaySynonym"
        assert result[2]["input"] == "dog"
        assert "puppy" in result[2]["synonyms"]
        assert "pup" in result[2]["synonyms"]

    def test_parse_synonyms_file_not_found(self):
        """Test _parse_synonyms_file when file is not found."""
        with patch("pathlib.Path.open", side_effect=FileNotFoundError):
            result = IndexBase._parse_synonyms_file("nonexistent.txt")
            assert result is None
            self.mock_logger.exception.assert_called_once_with(
                "Synonyms file not found", extra={"file_path": "nonexistent.txt"}
            )

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

            result = IndexBase.get_total_count(index_name)
            assert result == 0
            mock_logger.exception.assert_called_once()

    def test_get_total_count_with_filters(self):
        """Test get_total_count with search filters."""
        index_name = "test_index"
        search_filters = "category:books"

        mock_response = MagicMock()
        mock_response.nb_hits = TOTAL_COUNT
        self.mock_client.search_single_index.return_value = mock_response

        with patch("apps.common.index.settings") as mock_settings:
            mock_settings.ENVIRONMENT = "testenv"

            IndexBase.get_total_count.cache_clear()
            result = IndexBase.get_total_count(index_name, search_filters)

            assert result == TOTAL_COUNT
            self.mock_client.search_single_index.assert_called_once_with(
                index_name="testenv_test_index",
                search_params={
                    "analytics": False,
                    "hitsPerPage": 0,
                    "query": "",
                    "filters": "category:books",
                },
            )

    def test_reindex_synonyms(self):
        """Test reindex_synonyms method."""
        app_name = "test"
        index_name = "test_index"

        self.mock_client.clear_synonyms.return_value = {"taskID": 1}
        self.mock_client.save_synonyms.return_value = {"taskID": 2}

        with patch.object(
            IndexBase,
            "_parse_synonyms_file",
            return_value=[{"synonym1": "value1"}, {"synonym2": "value2"}],
        ):
            result = IndexBase.reindex_synonyms(app_name, index_name)

        assert result == EXPECTED_REINDEX_RESULT
        self.mock_client.clear_synonyms.assert_called_once_with(index_name="test_test_index")
        self.mock_client.save_synonyms.assert_called_once_with(
            index_name="test_test_index",
            synonym_hit=[{"synonym1": "value1"}, {"synonym2": "value2"}],
            replace_existing_synonyms=True,
        )

    def test_reindex_synonyms_file_not_found(self):
        """Test reindex_synonyms when file is not found."""
        app_name = "test"
        index_name = "test_index"

        with patch.object(IndexBase, "_parse_synonyms_file", return_value=None) as mock_parse:
            result = IndexBase.reindex_synonyms(app_name, index_name)

            assert result is None
            mock_parse.assert_called_once_with(
                Path("/test/base/dir/apps/test/index/synonyms/test_index.txt")
            )
            self.mock_client.clear_synonyms.assert_not_called()

    def test_reindex_synonyms_algolia_exception(self):
        """Test reindex_synonyms when Algolia throws an exception."""
        app_name = "test"
        index_name = "test_index"

        self.mock_client.clear_synonyms.side_effect = AlgoliaException("API Error")

        with patch.object(
            IndexBase,
            "_parse_synonyms_file",
            return_value=[{"synonym1": "value1"}],
        ):
            result = IndexBase.reindex_synonyms(app_name, index_name)

            assert result is None
            self.mock_logger.exception.assert_called_once_with(
                "Error saving synonyms for '%s'", "test_test_index"
            )


class TestIndexBaseGetQueryset:
    def test_get_queryset_local_build(self):
        with (
            patch("apps.common.index.IS_LOCAL_BUILD", new=True),
            patch.object(AlgoliaIndex, "__init__", return_value=None),
            patch.object(AlgoliaIndex, "get_entities", create=True),
        ):
            index = IndexBase()
            index.get_entities = MagicMock(return_value=["test_object"])
            result = index.get_queryset()
            assert result == ["test_object"]

    def test_get_queryset_local_build_empty_queryset(self):
        with (
            patch("apps.common.index.IS_LOCAL_BUILD", new=True),
            patch.object(AlgoliaIndex, "__init__", return_value=None),
            patch.object(AlgoliaIndex, "get_entities", create=True),
        ):
            index = IndexBase()
            index.get_entities = MagicMock(return_value=[])
            result = index.get_queryset()
            assert result == []

    def test_get_queryset_non_local_build(self):
        with (
            patch("apps.common.index.IS_LOCAL_BUILD", new=False),
            patch.object(AlgoliaIndex, "__init__", return_value=None),
            patch.object(AlgoliaIndex, "get_entities", create=True),
        ):
            index = IndexBase()
            mock_queryset = ["item1", "item2", "item3"]
            index.get_entities = MagicMock(return_value=mock_queryset)
            result = index.get_queryset()
            assert result == mock_queryset
