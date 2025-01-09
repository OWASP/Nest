"""Algolia index synonyms support and record count."""

import json
import logging
from functools import lru_cache
from pathlib import Path

from algoliasearch.http.exceptions import AlgoliaException
from algoliasearch.search.client import SearchClientSync
from django.conf import settings

logger = logging.getLogger(__name__)


class IndexBase:
    """Nest index synonyms mixin and record count."""

    @staticmethod
    def _get_client():
        """Get the Algolia client."""
        return SearchClientSync(
            settings.ALGOLIA_APPLICATION_ID,
            settings.ALGOLIA_WRITE_API_KEY,
        )

    @staticmethod
    def reindex_synonyms(app_name, index_name):
        """Reindex synonyms."""
        file_path = Path.open(
            f"{settings.BASE_DIR}/apps/{app_name}/index/synonyms/{index_name}.json"
        )
        try:
            synonyms = json.load(file_path)
        except FileNotFoundError:
            logger.exception("Synonyms file not found", extra={"file_path": file_path})
            return None

        for idx, synonym in enumerate(synonyms, 1):
            synonym["objectID"] = f"{index_name}-synonym-{idx}"
            # Set default type to regular (two-way) synonym.
            if "type" not in synonym:
                synonym["type"] = "synonym"

        client = IndexBase._get_client()
        index_name = f"{settings.ENVIRONMENT.lower()}_{index_name}"

        client.clear_synonyms(index_name=index_name)
        client.save_synonyms(
            index_name=index_name, synonym_hit=synonyms, replace_existing_synonyms=True
        )

        return len(synonyms)

    @staticmethod
    @lru_cache(maxsize=1024)
    def get_total_count(index_name):
        """Get total count of records in index."""
        client = IndexBase._get_client()
        try:
            return client.search_single_index(
                index_name=f"{settings.ENVIRONMENT.lower()}_{index_name}",
                search_params={"query": "", "hitsPerPage": 0, "analytics": False},
            ).nb_hits
        except AlgoliaException:
            logger.exception("Error retrieving index count for '%s'", index_name)
            return 0
