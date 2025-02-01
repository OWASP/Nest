"""Algolia index synonyms support and record count."""

import logging
from functools import lru_cache
from pathlib import Path

from algoliasearch.http.exceptions import AlgoliaException
from algoliasearch.search.client import SearchClientSync
from django.conf import settings

from apps.common.constants import NL

logger = logging.getLogger(__name__)

IS_LOCAL_BUILD = settings.ENVIRONMENT == "Local"
LOCAL_INDEX_LIMIT = 1000


class IndexBase:
    """Nest index synonyms mixin and record count."""

    @staticmethod
    def get_client():
        """Get the Algolia client."""
        return SearchClientSync(
            settings.ALGOLIA_APPLICATION_ID,
            settings.ALGOLIA_WRITE_API_KEY,
        )

    @staticmethod
    def _parse_synonyms_file(file_path):
        """Parse synonyms file."""
        try:
            with Path(file_path).open("r", encoding="utf-8") as f:
                file_content = f.read()
        except FileNotFoundError:
            logger.exception("Synonyms file not found", extra={"file_path": file_path})
            return None

        synonyms = []
        for idx, line in enumerate(file_content.strip().split(NL), 1):
            cleaned_line = line.strip()
            if not cleaned_line or cleaned_line.startswith("#"):
                continue

            if ":" in cleaned_line:  # one-way synonym
                input_term, synonyms_str = cleaned_line.split(":", 1)
                input_term = input_term.strip()
                synonyms.append(
                    {
                        "objectID": f"{idx}",
                        "type": "oneWaySynonym",
                        "input": input_term,
                        "synonyms": [t for term in synonyms_str.split(",") if (t := term.strip())],
                    }
                )
            else:  # regular two-way synonym
                synonyms.append(
                    {
                        "objectID": f"{idx}",
                        "type": "synonym",
                        "synonyms": [t for term in cleaned_line.split(",") if (t := term.strip())],
                    }
                )

        return synonyms

    @staticmethod
    def reindex_synonyms(app_name, index_name):
        """Reindex synonyms."""
        file_path = Path(f"{settings.BASE_DIR}/apps/{app_name}/index/synonyms/{index_name}.txt")

        if not (synonyms := IndexBase._parse_synonyms_file(file_path)):
            return None

        client = IndexBase.get_client()
        index_name = f"{settings.ENVIRONMENT.lower()}_{index_name}"

        try:
            client.clear_synonyms(index_name=index_name)
            client.save_synonyms(
                index_name=index_name, synonym_hit=synonyms, replace_existing_synonyms=True
            )
        except AlgoliaException:
            logger.exception("Error saving synonyms for '%s'", index_name)
            return None

        return len(synonyms)

    @staticmethod
    @lru_cache(maxsize=1024)
    def get_total_count(index_name, filter_condition=None):
        """Get total count of records in index."""
        client = IndexBase.get_client()
        try:
            search_params = {
                "query": "",
                "hitsPerPage": 0,
                "analytics": False,
            }
            if filter_condition:
                search_params["filters"] = filter_condition
            return client.search_single_index(
                index_name=f"{settings.ENVIRONMENT.lower()}_{index_name}",
                search_params=search_params,
            ).nb_hits
        except AlgoliaException:
            logger.exception("Error retrieving index count for '%s'", index_name)
            return 0
