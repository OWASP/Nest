from unittest.mock import MagicMock, mock_open, patch

import pytest
from algoliasearch.http.exceptions import AlgoliaException

from apps.common.index import IndexBase


class MockSearchResponse:
    def __init__(self, nb_hits):
        self.nb_hits = nb_hits


class TestIndexBase:
    @pytest.mark.parametrize(
        ("file_content", "expected_synonyms"),
        [
            (
                """laptop: notebook, portable computer
desktop, workstation, pc
tablet: ipad, slate""",
                [
                    {
                        "objectID": "test_index-synonym-1",
                        "type": "oneWaySynonym",
                        "input": "laptop",
                        "synonyms": ["notebook", "portable computer"],
                    },
                    {
                        "objectID": "test_index-synonym-2",
                        "type": "synonym",
                        "synonyms": ["desktop", "workstation", "pc"],
                    },
                    {
                        "objectID": "test_index-synonym-3",
                        "type": "oneWaySynonym",
                        "input": "tablet",
                        "synonyms": ["ipad", "slate"],
                    },
                ],
            ),
            (
                """# Comment line
word1, word2

key: value1, value2""",
                [
                    {
                        "objectID": "test_index-synonym-2",
                        "type": "synonym",
                        "synonyms": ["word1", "word2"],
                    },
                    {
                        "objectID": "test_index-synonym-4",
                        "type": "oneWaySynonym",
                        "input": "key",
                        "synonyms": ["value1", "value2"],
                    },
                ],
            ),
            (
                """main: synonym1, synonym2
key: value1, value2""",
                [
                    {
                        "objectID": "test_index-synonym-1",
                        "type": "oneWaySynonym",
                        "input": "main",
                        "synonyms": ["synonym1", "synonym2"],
                    },
                    {
                        "objectID": "test_index-synonym-2",
                        "type": "oneWaySynonym",
                        "input": "key",
                        "synonyms": ["value1", "value2"],
                    },
                ],
            ),
        ],
    )
    def test_reindex_synonyms(self, file_content, expected_synonyms):
        app_name = "test_app"
        index_name = "test_index"

        with (
            patch("apps.common.index.settings") as mock_settings,
            patch("apps.common.index.logger") as mock_logger,
            patch("apps.common.index.SearchClientSync") as mock_search_client,
            patch("pathlib.Path.open", mock_open(read_data=file_content)),
        ):
            mock_settings.BASE_DIR = "/base/dir"
            mock_settings.ENVIRONMENT = "testenv"
            mock_settings.ALGOLIA_APPLICATION_ID = "test_app_id"
            mock_settings.ALGOLIA_WRITE_API_KEY = "test_api_key"

            mock_client = MagicMock()
            mock_search_client.return_value = mock_client

            result = IndexBase.reindex_synonyms(app_name, index_name)

            mock_client.clear_synonyms.assert_called_once_with(index_name="testenv_test_index")

            mock_client.save_synonyms.assert_called_once()
            call_args = mock_client.save_synonyms.call_args
            assert call_args.kwargs["index_name"] == "testenv_test_index"
            assert call_args.kwargs["synonym_hit"] == expected_synonyms
            assert call_args.kwargs["replace_existing_synonyms"] is True

            assert result == len(expected_synonyms)
            mock_logger.exception.assert_not_called()

    def test_reindex_synonyms_save_error(self):
        app_name = "test_app"
        index_name = "test_index"
        file_content = "word1, word2"

        with (
            patch("apps.common.index.settings") as mock_settings,
            patch("apps.common.index.logger") as mock_logger,
            patch("apps.common.index.SearchClientSync") as mock_search_client,
            patch("pathlib.Path.open", mock_open(read_data=file_content)),
        ):
            mock_settings.BASE_DIR = "/base/dir"
            mock_settings.ENVIRONMENT = "testenv"
            mock_settings.ALGOLIA_APPLICATION_ID = "test_app_id"
            mock_settings.ALGOLIA_WRITE_API_KEY = "test_api_key"

            mock_client = MagicMock()
            mock_client.save_synonyms.side_effect = AlgoliaException("API Error")
            mock_search_client.return_value = mock_client

            result = IndexBase.reindex_synonyms(app_name, index_name)

            assert result is None
            mock_logger.exception.assert_called_once_with(
                "Error saving synonyms for '%s'", "testenv_test_index"
            )

    def test_get_total_count_success(self):
        index_name = "test_index"
        expected_hits = 42

        with (
            patch("apps.common.index.settings") as mock_settings,
            patch("apps.common.index.SearchClientSync") as mock_search_client,
        ):
            mock_settings.ENVIRONMENT = "testenv"
            mock_settings.ALGOLIA_APPLICATION_ID = "test_app_id"
            mock_settings.ALGOLIA_WRITE_API_KEY = "test_api_key"

            mock_client = MagicMock()
            mock_client.search_single_index.return_value = MockSearchResponse(expected_hits)
            mock_search_client.return_value = mock_client

            result = IndexBase.get_total_count(index_name)

            assert result == expected_hits
            mock_client.search_single_index.assert_called_once_with(
                index_name="testenv_test_index",
                search_params={"query": "", "hitsPerPage": 0, "analytics": False},
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
