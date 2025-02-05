"""Algolia index synonyms support and record count."""

import logging
import os
from functools import lru_cache
from pathlib import Path

from algoliasearch.http.exceptions import AlgoliaException
from algoliasearch.query_suggestions.client import QuerySuggestionsClientSync
from algoliasearch.search.client import SearchClientSync
from algoliasearch_django.decorators import register as algolia_register
from django.conf import settings

from apps.common.constants import NL

logger = logging.getLogger(__name__)

IS_LOCAL_BUILD = settings.ENVIRONMENT.lower() == "local"
LOCAL_INDEX_LIMIT = 1000


class IndexRegistry:
    """Registry to track and manage Algolia indices."""

    _instance = None

    def __init__(self):
        """Initialize the IndexRegistry with empty sets and load excluded patterns."""
        self.excluded_patterns = set()
        self.excluded_models = set()
        self.reload_excluded_patterns()

    @classmethod
    def get_instance(cls):
        """Get or create a singleton instance of IndexRegistry."""
        if not cls._instance:
            cls._instance = IndexRegistry()
        return cls._instance

    def reload_excluded_patterns(self):
        """Load excluded patterns and models from environment."""
        excluded_str = os.getenv("ALGOLIA_EXCLUDED_INDICES", "").strip()
        self.excluded_patterns = {
            pattern.strip().lower() for pattern in excluded_str.split(",") if pattern.strip()
        }

        excluded_models = os.getenv("ALGOLIA_EXCLUDED_MODELS", "").strip()
        self.excluded_models = {
            model.strip().lower() for model in excluded_models.split(",") if model.strip()
        }

    def is_excluded(self, name: str, check_type: str = "index"):
        """Check if an index name matches any excluded pattern."""
        name = name.lower()

        if check_type == "suggestion":
            base_name = name.replace("_suggestions", "")
            return any(
                pattern in base_name or pattern in name for pattern in self.excluded_patterns
            )

        if check_type == "model":
            return name in self.excluded_models

        return any(pattern in name for pattern in self.excluded_patterns)


def should_create_index(index_name: str, index_type: str = "index"):
    """Determine if an index should be created based on configuration."""
    if not IS_LOCAL_BUILD:
        return True

    registry = IndexRegistry.get_instance()

    if index_type == "suggestion" and registry.is_excluded(index_name, "suggestion"):
        return False

    return not registry.is_excluded(index_name)


def conditional_register(model, **kwargs):
    """Register an Algolia index conditionally based on configuration."""

    def decorator(index_cls):
        model_path = f"{model._meta.app_label}/{model._meta.model_name}".lower()

        registry = IndexRegistry.get_instance()
        if registry.is_excluded(model_path, "model"):
            return index_cls

        full_index_name = f"{settings.ENVIRONMENT.lower()}_{index_cls.index_name}"

        if should_create_index(full_index_name):
            return algolia_register(model, **kwargs)(index_cls)

        return index_cls

    return decorator


class IndexBase:
    """Base index class with enhanced functionality."""

    @staticmethod
    def get_client():
        """Return an instance of the Algolia search client."""
        return SearchClientSync(settings.ALGOLIA_APPLICATION_ID, settings.ALGOLIA_WRITE_API_KEY)

    @staticmethod
    def get_suggestions_client():
        """Get the Algolia suggestions client."""
        return QuerySuggestionsClientSync(
            settings.ALGOLIA_APPLICATION_ID,
            settings.ALGOLIA_WRITE_API_KEY,
            getattr(settings, "ALGOLIA_APPLICATION_REGION", None),
        )

    @staticmethod
    def configure_replicas(env: str, base_index: str, replicas: dict):
        """Configure replica indices with selective creation based on environment."""
        client = IndexBase.get_client()
        base_index_name = f"{env}_{base_index}"

        if not should_create_index(base_index_name):
            return

        if not IS_LOCAL_BUILD:
            replica_names = list(replicas.keys())
            client.set_settings(base_index_name, {"replicas": replica_names})
            for replica_name, ranking in replicas.items():
                client.set_settings(replica_name, {"ranking": ranking})
            return

        filtered_replicas = {
            name: ranking
            for name, ranking in replicas.items()
            if should_create_index(name, "replica")
        }

        client.set_settings(
            base_index_name,
            {"replicas": list(filtered_replicas.keys()) if filtered_replicas else []},
        )

        for replica_name, ranking in filtered_replicas.items():
            client.set_settings(replica_name, {"ranking": ranking})

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
    def get_total_count(index_name):
        """Get total count of records in index."""
        client = IndexBase.get_client()
        try:
            return client.search_single_index(
                index_name=f"{settings.ENVIRONMENT.lower()}_{index_name}",
                search_params={"query": "", "hitsPerPage": 0, "analytics": False},
            ).nb_hits
        except AlgoliaException:
            logger.exception("Error retrieving index count for '%s'", index_name)
            return 0
