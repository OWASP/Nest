from unittest.mock import MagicMock, mock_open, patch

import pytest
from algoliasearch.exceptions import AlgoliaException

from apps.common.index import IndexBase


class TestIndexBase:
    @pytest.mark.parametrize(
        ("app_name", "index_name", "synonyms_data", "expected_synonym"),
        [
            (
                "app1",
                "index1",
                [{"synonym": "synonym1"}],
                [{"objectID": "index1-synonym-1", "synonym": "synonym1", "type": "synonym"}],
            ),
            (
                "app2",
                "index2",
                [{"synonym": "synonym2", "type": "oneWaySynonym"}],
                [{"objectID": "index2-synonym-1", "synonym": "synonym2", "type": "oneWaySynonym"}],
            ),
        ],
    )
    @patch("apps.common.index.Path.open", new_callable=mock_open)
    @patch("apps.common.index.IndexBase._get_client")
    @patch("apps.common.index.settings")
    @patch("apps.common.index.json.load")
    def test_reindex_synonyms(
        self,
        mock_json_load,
        mock_settings,
        mock_get_client,
        mock_open,
        app_name,
        index_name,
        synonyms_data,
        expected_synonym,
    ):
        mock_settings.ENVIRONMENT.lower.return_value = "testenv"
        mock_settings.BASE_DIR = "/base/dir"
        mock_json_load.return_value = synonyms_data

        mock_index = MagicMock()
        mock_get_client.return_value.init_index.return_value = mock_index

        expected_file_path = f"/base/dir/apps/{app_name}/index/synonyms/{index_name}.json"

        with patch("apps.common.index.logger"):
            IndexBase.reindex_synonyms(app_name, index_name)

        mock_open.assert_called_once_with(expected_file_path)
        mock_index.clear_synonyms.assert_called_once()
        mock_index.save_synonyms.assert_called_once_with(
            expected_synonym, {"replaceExistingSynonyms": True}
        )

    @pytest.mark.parametrize(
        ("index_name", "search_response", "expected_count"),
        [
            ("index1", {"nbHits": 5}, 5),
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

        mock_index = MagicMock()
        mock_get_client.return_value.init_index.return_value = mock_index

        if isinstance(search_response, dict):
            mock_index.search.return_value = search_response
        else:
            mock_index.search.side_effect = search_response

        count = IndexBase.get_total_count(index_name)

        assert count == expected_count
        if isinstance(search_response, dict):
            mock_index.search.assert_called_once_with("", {"hitsPerPage": 0, "analytics": False})
        else:
            mock_logger.exception.assert_called_once_with(
                "Error retrieving index count for '%s'", index_name
            )
