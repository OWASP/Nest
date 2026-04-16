"""Algolia index common classes and helpers."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from algoliasearch.http.exceptions import AlgoliaException
from algoliasearch.search.client import SearchClientSync
from algoliasearch.search.config import SearchConfig
from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register as algolia_register
from django.conf import settings

from apps.common.constants import NL

logger: logging.Logger = logging.getLogger(__name__)

EXCLUDED_LOCAL_INDEX_NAMES = (
    "projects_contributors_count_asc",
    "projects_contributors_count_desc",
    "projects_forks_count_asc",
    "projects_forks_count_desc",
    "projects_level_raw_asc",
    "projects_level_raw_desc",
    "projects_name_asc",
    "projects_name_desc",
    "projects_stars_count_asc",
    "projects_stars_count_desc",
    "projects_updated_at_asc",
    "projects_updated_at_desc",
)
LOCAL_INDEX_LIMIT = 1000


class IndexRegistry:
    """Registry to track and manage Algolia indices."""

    _instance = None

    def __init__(self) -> None:
        """Initialize index registry."""
        self.excluded_local_index_names: set = set()
        self.load_excluded_local_index_names()

    @classmethod
    def get_instance(cls) -> IndexRegistry:
        """Get or create a singleton instance of IndexRegistry."""
        if cls._instance is None:
            cls._instance = IndexRegistry()
        return cls._instance

    def is_indexable(self, name: str) -> bool:
        """Check if an index is enabled for indexing.

        Args:
            name (str): The name of the index.

        Returns:
            bool: True if the index is enabled, False otherwise.

        """
        return (
            name.lower() not in self.excluded_local_index_names
            if settings.IS_LOCAL_ENVIRONMENT
            else True
        )

    def load_excluded_local_index_names(self) -> IndexRegistry:
        """Load excluded local index names from settings.

        Returns
            IndexRegistry: The current instance of the registry.

        """
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


def is_indexable(index_name: str) -> bool:
    """Determine if an index should be created based on configuration.

    Args:
        index_name (str): The name of the index.

    Returns:
        bool: True if the index is indexable, False otherwise.

    """
    return IndexRegistry.get_instance().is_indexable(index_name)


def register(model, **kwargs):
    """Register an index if configuration allows.

    Args:
        model (Model): The Django model to register.
        **kwargs: Additional arguments for the registration.

    Returns:
        Callable: A wrapper function for the index class.

    """

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
    def get_client(ip_address=None) -> SearchClientSync:
        """Return an instance of the search client.

        Args:
            ip_address (str, optional): The IP address for the client.

        Returns:
            SearchClientSync: The search client instance.

        """
        config = SearchConfig(
            settings.ALGOLIA_APPLICATION_ID,
            settings.ALGOLIA_WRITE_API_KEY,
        )
        if ip_address is not None:
            config.headers["X-Forwarded-For"] = ip_address

        return SearchClientSync(config=config)

    @staticmethod
    def configure_replicas(index_name: str, replicas: dict) -> None:
        """Configure replicas for an index.

        Args:
            index_name (str): The name of the base index.
            replicas (dict): A dictionary of replica names and their ranking configurations.

        """
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
    def _parse_synonyms_file(file_path) -> list | None:
        """Parse a synonyms file and return its content.

        Args:
            file_path (str): The path to the synonyms file.

        Returns:
            list: A list of parsed synonyms or None if the file is not found.

        """
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
    def reindex_synonyms(app_name: str, index_name: str) -> int | None:
        """Reindex synonyms for a specific index.

        Args:
            app_name (str): The name of the application.
            index_name (str): The name of the index.

        Returns:
            int or None: The number of synonyms reindexed, or None if an error occurs.

        """
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
    def get_total_count(index_name: str, search_filters=None) -> int | None:
        """Get the total count of records in an index.

        Args:
            index_name (str): The name of the index.
            search_filters (str, optional): Filters to apply to the search.

        Returns:
            int: The total count of records in the index.

        """
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
        """Get the queryset for the index.

        Returns
            QuerySet: The queryset of entities to index.

        """
        qs = self.get_entities()

        return qs[:LOCAL_INDEX_LIMIT] if settings.IS_LOCAL_ENVIRONMENT else qs
