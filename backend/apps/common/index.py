"""Algolia index synonyms support and record count."""

import json
import logging
from functools import lru_cache
from pathlib import Path

from algoliasearch.exceptions import AlgoliaException
from algoliasearch.search_client import SearchClient
from django.conf import settings

logger = logging.getLogger(__name__)


class IndexBase:
    """Nest index synonyms mixin and record count."""

    @staticmethod
    def _get_client():
        """Get the Algolia client."""
        return SearchClient.create(
            settings.ALGOLIA_APPLICATION_ID,
            settings.ALGOLIA_API_KEY,
        )

    @staticmethod
    def reindex_synonyms(app_name, index_name):
        """Reindex synonyms."""
        index = IndexBase._get_client().init_index(f"{settings.ENVIRONMENT.lower()}_{index_name}")

        file_path = Path.open(
            f"{settings.BASE_DIR}/apps/{app_name}/index/synonyms/{index_name}.json"
        )
        try:
            synonyms = json.load(file_path)
        except FileNotFoundError:
            logger.exception("Synonyms file not found", extra={"file_path": file_path})
            return

        for idx, synonym in enumerate(synonyms, 1):
            synonym["objectID"] = f"{index_name}-synonym-{idx}"
            # Set default type to regular (two-way) synonym.
            if "type" not in synonym:
                synonym["type"] = "synonym"

        index.clear_synonyms()
        index.save_synonyms(synonyms, {"replaceExistingSynonyms": True})

    @staticmethod
    @lru_cache(maxsize=1024)
    def get_total_count(index_name):
        """Get total count of records in index."""
        try:
            index = IndexBase._get_client().init_index(
                f"{settings.ENVIRONMENT.lower()}_{index_name}"
            )
            return index.search("", {"hitsPerPage": 0, "analytics": False})["nbHits"]

        except AlgoliaException:
            logger.exception("Error retrieving index count for '%s'", index_name)
            return 0
