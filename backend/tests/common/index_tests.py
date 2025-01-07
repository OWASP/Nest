from unittest.mock import MagicMock, patch

import pytest
from algoliasearch.http.exceptions import AlgoliaException

from apps.common.index import IndexBase


class MockSearchResponse:
    def __init__(self, nb_hits):
        self.nb_hits = nb_hits


class TestIndexBase:
    @pytest.mark.parametrize(
        ("synonyms_data", "expected_enriched_synonyms"),
        [
            (
                [{"type": "synonym", "synonyms": ["word1", "word2"]}],
                [
                    {
                        "type": "synonym",
                        "synonyms": ["word1", "word2"],
                        "objectID": "test_index-synonym-1",
                    }
                ],
            ),
            (
                [
                    {"type": "synonym", "synonyms": ["word1", "word2"]},
                    {"synonyms": ["term1", "term2"]},
                ],
                [
                    {
                        "type": "synonym",
                        "synonyms": ["word1", "word2"],
                        "objectID": "test_index-synonym-1",
                    },
                    {
                        "type": "synonym",
                        "synonyms": ["term1", "term2"],
                        "objectID": "test_index-synonym-2",
                    },
                ],
            ),
        ],
    )
    @patch("apps.common.index.json.load")
    @patch("apps.common.index.Path.open")
    @patch("apps.common.index.IndexBase._get_client")
    @patch("apps.common.index.logger")
    @patch("apps.common.index.settings")
    def test_reindex_synonyms(
        self,
        mock_settings,
        mock_logger,
        mock_get_client,
        mock_open_path,
        mock_json_load,
        synonyms_data,
        expected_enriched_synonyms,
    ):
        app_name = "test_app"
        index_name = "test_index"
        file_path = f"/apps/{app_name}/index/synonyms/{index_name}.json"

        mock_settings.BASE_DIR = "/base/dir"
        mock_settings.ENVIRONMENT.lower.return_value = "testenv"

        mock_open_path.return_value.__enter__.return_value = MagicMock()
        mock_json_load.return_value = synonyms_data

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        IndexBase.reindex_synonyms(app_name, index_name)

        mock_open_path.assert_called_once_with(f"/base/dir{file_path}")

        mock_client.clear_synonyms.assert_called_once_with(index_name="testenv_test_index")
        mock_client.save_synonyms.assert_called_once_with(
            index_name="testenv_test_index",
            synonym_hit=expected_enriched_synonyms,
            replace_existing_synonyms=True,
        )

        mock_logger.exception.assert_not_called()

    @pytest.mark.parametrize(
        ("index_name", "search_response", "expected_count"),
        [
            ("index1", MockSearchResponse(5), 5),
            ("index2", AlgoliaException("Error"), 0),
        ],
    )
    @patch("apps.common.index.IndexBase._get_client")
    @patch("apps.common.index.logger")
    @patch("apps.common.index.settings")
    def test_get_total_count(
        self,
        mock_settings,
        mock_logger,
        mock_get_client,
        index_name,
        search_response,
        expected_count,
    ):
        mock_settings.ENVIRONMENT.lower.return_value = "testenv"

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        if isinstance(search_response, MockSearchResponse):
            mock_client.search_single_index.return_value = search_response
        else:
            mock_client.search_single_index.side_effect = search_response

        count = IndexBase.get_total_count(index_name)

        assert count == expected_count
        if isinstance(search_response, MockSearchResponse):
            mock_client.search_single_index.assert_called_once_with(
                index_name=f"testenv_{index_name}",
                search_params={"query": "", "hitsPerPage": 0, "analytics": False},
            )
            mock_logger.exception.assert_not_called()
        else:
            mock_logger.exception.assert_called_once_with(
                "Error retrieving index count for '%s'", index_name
            )
