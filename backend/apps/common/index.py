"""Algolia index synonyms support."""

import json
import logging
from functools import lru_cache
from pathlib import Path

from algoliasearch.search_client import SearchClient
from django.conf import settings

logger = logging.getLogger(__name__)


class IndexSynonymsMixin:
    """Nest index synonyms mixin."""

    @staticmethod
    def _get_algolia_client():
        """Reusable method to get the Algolia client."""
        return SearchClient.create(
            settings.ALGOLIA_APPLICATION_ID,
            settings.ALGOLIA_API_KEY,
        )

    @staticmethod
    def reindex_synonyms(app_name, index_name):
        """Reindex synonyms."""
        index = IndexSynonymsMixin._get_algolia_client().init_index(
            f"{settings.ENVIRONMENT.lower()}_{index_name}"
        )

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
    def get_algolia_index_count(index_name):
        """Get the number of records in an Algolia index."""
        try:
            index = IndexSynonymsMixin._get_algolia_client().init_index(index_name)
            return index.search("", {"hitsPerPage": 0, "analytics": False})["nbHits"]

        except Exception:
            logger.exception("Error retrieving index count for '%s'", index_name)
            return None
