"""Algolia index common classes and helpers."""

import logging
from functools import lru_cache
from pathlib import Path

from algoliasearch.http.exceptions import AlgoliaException
from algoliasearch.query_suggestions.client import QuerySuggestionsClientSync
from algoliasearch.search.client import SearchClientSync
from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register as algolia_register
from django.conf import settings

from apps.common.constants import NL

logger = logging.getLogger(__name__)

EXCLUDED_LOCAL_INDEX_NAMES = (
    "chapters_suggestions",
    "committees_suggestions",
    "issues_suggestions",
    "projects_contributors_count_asc",
    "projects_contributors_count_desc",
    "projects_forks_count_asc",
    "projects_forks_count_desc",
    "projects_name_asc",
    "projects_name_desc",
    "projects_query_suggestions",
    "projects_stars_count_asc",
    "projects_stars_count_desc",
    "projects_suggestions",
    "users_suggestions",
)
IS_LOCAL_BUILD = settings.ENVIRONMENT == "Local"
LOCAL_INDEX_LIMIT = 1000


class IndexRegistry:
    """Registry to track and manage Algolia indices."""

    _instance = None

    def __init__(self):
        """Initialize index registry."""
        self.excluded_local_index_names = set()
        self.load_excluded_local_index_names()

    @classmethod
    def get_instance(cls):
        """Get or create a singleton instance of IndexRegistry."""
        if cls._instance is None:
            cls._instance = IndexRegistry()
        return cls._instance

    def is_indexable(self, name: str):
        """Check if index is on."""
        return name.lower() not in self.excluded_local_index_names if IS_LOCAL_BUILD else True

    def load_excluded_local_index_names(self):
        """Load excluded local index names."""
        excluded_names = settings.ALGOLIA_EXCLUDED_LOCAL_INDEX_NAMES
        self.excluded_local_index_names = set(
            (
                excluded_name.strip().lower()
                for excluded_name in excluded_names.strip().split(",")
                if excluded_name.strip()
            )
            if excluded_names and excluded_names != "None"
            else EXCLUDED_LOCAL_INDEX_NAMES
        )

        return self


def is_indexable(index_name: str):
    """Determine if an index should be created based on configuration."""
    return IndexRegistry.get_instance().is_indexable(index_name)


def register(model, **kwargs):
    """Register index if configuration allows."""

    def wrapper(index_cls):
        return (
            algolia_register(model, **kwargs)(index_cls)
            if is_indexable(f"{index_cls.index_name}")
            else index_cls
        )

    return wrapper


class IndexBase(AlgoliaIndex):
    """Base index class."""

    @staticmethod
    def get_client():
        """Return an instance of search client."""
        return SearchClientSync(
            settings.ALGOLIA_APPLICATION_ID,
            settings.ALGOLIA_WRITE_API_KEY,
        )

    @staticmethod
    def get_suggestions_client():
        """Get suggestions client."""
        return QuerySuggestionsClientSync(
            settings.ALGOLIA_APPLICATION_ID,
            settings.ALGOLIA_WRITE_API_KEY,
            getattr(settings, "ALGOLIA_APPLICATION_REGION", None),
        )

    @staticmethod
    def configure_replicas(index_name: str, replicas: dict):
        """Configure replicas."""
        if not is_indexable(index_name):
            return  # Skip replicas configuration if base index is off.

        env = settings.ENVIRONMENT.lower()

        if indexable_replicas := {
            f"{env}_{index_name}_{replica_name}": replica_ranking
            for replica_name, replica_ranking in replicas.items()
            if is_indexable(f"{index_name}_{replica_name}")
        }:
            client = IndexBase.get_client()
            client.set_settings(
                f"{env}_{index_name}",
                {"replicas": sorted(indexable_replicas.keys())},
            )

            for replica_name, replica_ranking in indexable_replicas.items():
                client.set_settings(replica_name, {"ranking": replica_ranking})

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
    def get_total_count(index_name, search_filters=None):
        """Get total count of records in index."""
        client = IndexBase.get_client()
        try:
            search_params = {
                "analytics": False,
                "hitsPerPage": 0,
                "query": "",
            }
            if search_filters:
                search_params["filters"] = search_filters
            return client.search_single_index(
                index_name=f"{settings.ENVIRONMENT.lower()}_{index_name}",
                search_params=search_params,
            ).nb_hits
        except AlgoliaException:
            logger.exception("Error retrieving index count for '%s'", index_name)
            return 0

    def get_queryset(self):
        """Get queryset."""
        qs = self.get_entities()

        return qs[:LOCAL_INDEX_LIMIT] if IS_LOCAL_BUILD else qs
