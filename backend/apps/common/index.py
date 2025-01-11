"""Algolia index synonyms support and record count."""

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
    def _parse_synonyms_file(file_path, index_name):
        """Parse synonyms from txt file."""
        try:
            with Path(file_path).open("r", encoding="utf-8") as f:
                file_content = f.read()
        except FileNotFoundError:
            logger.exception("Synonyms file not found", extra={"file_path": file_path})
            return None

        synonyms = []
        for idx, original_line in enumerate(file_content.strip().split("\n"), 1):
            cleaned_line = original_line.strip()
            if not cleaned_line or cleaned_line.startswith("#"):
                continue

            if ":" in cleaned_line:
                input_term, synonyms_str = cleaned_line.split(":", 1)
                input_term = input_term.strip()
                synonym_terms = [term.strip() for term in synonyms_str.split(",")]
                synonyms.append(
                    {
                        "objectID": f"{index_name}-synonym-{idx}",
                        "type": "oneWaySynonym",
                        "input": input_term,
                        "synonyms": [term for term in synonym_terms if term],
                    }
                )
            else:
                terms = [term.strip() for term in cleaned_line.split(",") if term.strip()]
                synonyms.append(
                    {
                        "objectID": f"{index_name}-synonym-{idx}",
                        "type": "synonym",
                        "synonyms": [term for term in terms if term],
                    }
                )

        return synonyms

    @staticmethod
    def reindex_synonyms(app_name, index_name):
        """Reindex synonyms."""
        file_path = Path(f"{settings.BASE_DIR}/apps/{app_name}/index/synonyms/{index_name}.txt")

        synonyms = IndexBase._parse_synonyms_file(file_path, index_name)
        if not synonyms:
            return None

        client = IndexBase._get_client()
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
