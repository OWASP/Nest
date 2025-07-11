"""Index utils."""

import contextlib

from algoliasearch_django import register, unregister
from algoliasearch_django.registration import RegistrationError
from django.apps import apps

from apps.common.utils import convert_to_camel_case


class DisableIndexing:
    """Context manager to temporarily disable Algolia indexing."""

    def __init__(self, app_names: tuple[str, ...] | None = None):
        """Initialize the context manager.

        Args:
            app_names: Optional tuple of app names to disable indexing for.
                      Defaults to ("github", "owasp") if None.

        """
        self.app_names = app_names or ("github", "owasp")

    def __enter__(self):
        """Disable indexing when entering the context."""
        self.unregister_indexes()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Re-enable indexing when exiting the context."""
        self.register_indexes()

    def register_indexes(self) -> None:
        """Register indexes.

        Args:
            app_names (tuple): A tuple of app names to register indexes for.

        """
        for app_name in self.app_names:
            for model in apps.get_app_config(app_name).get_models():
                with contextlib.suppress(RegistrationError):
                    register(model)

    def unregister_indexes(self) -> None:
        """Unregister indexes.

        Args:
            app_names (tuple): A tuple of app names to unregister indexes for.

        """
        for app_name in self.app_names:
            for model in apps.get_app_config(app_name).get_models():
                with contextlib.suppress(RegistrationError):
                    unregister(model)


def deep_camelize(obj) -> dict | list:
    """Deep camelize.

    Args:
        obj: The object to camelize.

    Returns:
        The camelize object.

    """
    if isinstance(obj, dict):
        return {
            convert_to_camel_case(key.removeprefix("idx_")): deep_camelize(value)
            for key, value in obj.items()
        }
    if isinstance(obj, list):
        return [deep_camelize(item) for item in obj]
    return obj


def disable_indexing(app_names: tuple[str, ...] | None = None) -> DisableIndexing:
    """Create a DisableIndexing context manager.

    Args:
        app_names: Optional tuple of app names to disable indexing for.
                  Defaults to ("github", "owasp") if None.

    Returns:
        A DisableIndexing context manager instance.

    Usage:
        with disable_indexing():
            # Perform operations without automatic indexing
            sync_repositories()
            update_entities()
        # Indexing is automatically re-enabled here

    """
    return DisableIndexing(app_names)


def get_params_for_index(index_name: str) -> dict:
    """Return search parameters based on the index name.

    Args:
        index_name (str): The name of the index.

    Returns:
        dict: The search parameters for the index.

    """
    params = {
        "attributesToHighlight": [],
        "removeWordsIfNoResults": "allOptional",
        "minProximity": 4,
        "typoTolerance": "min",
    }

    match index_name:
        case "issues":
            params["attributesToRetrieve"] = [
                "idx_comments_count",
                "idx_created_at",
                "idx_hint",
                "idx_labels",
                "idx_project_name",
                "idx_project_url",
                "idx_repository_languages",
                "idx_summary",
                "idx_title",
                "idx_updated_at",
                "idx_url",
            ]
            params["distinct"] = 1

        case "chapters":
            params["attributesToRetrieve"] = [
                "_geoloc",
                "idx_created_at",
                "idx_is_active",
                "idx_key",
                "idx_leaders",
                "idx_name",
                "idx_region",
                "idx_related_urls",
                "idx_suggested_location",
                "idx_summary",
                "idx_tags",
                "idx_top_contributors",
                "idx_updated_at",
                "idx_url",
            ]
            params["aroundLatLngViaIP"] = True

        case "projects":
            params["attributesToRetrieve"] = [
                "idx_contributors_count",
                "idx_forks_count",
                "idx_is_active",
                "idx_issues_count",
                "idx_key",
                "idx_languages",
                "idx_leaders",
                "idx_level",
                "idx_name",
                "idx_organizations",
                "idx_repositories_count",
                "idx_repositories",
                "idx_stars_count",
                "idx_summary",
                "idx_top_contributors",
                "idx_topics",
                "idx_type",
                "idx_updated_at",
                "idx_url",
            ]

        case "committees":
            params["attributesToRetrieve"] = [
                "idx_created_at",
                "idx_key",
                "idx_leaders",
                "idx_name",
                "idx_related_urls",
                "idx_summary",
                "idx_top_contributors",
                "idx_updated_at",
                "idx_url",
            ]

        case "users":
            params["attributesToRetrieve"] = [
                "idx_avatar_url",
                "idx_bio",
                "idx_company",
                "idx_created_at",
                "idx_email",
                "idx_followers_count",
                "idx_following_count",
                "idx_key",
                "idx_location",
                "idx_login",
                "idx_name",
                "idx_public_repositories_count",
                "idx_title",
                "idx_updated_at",
                "idx_url",
            ]

        case "organizations":
            params["attributesToRetrieve"] = [
                "idx_avatar_url",
                "idx_collaborators_count",
                "idx_created_at",
                "idx_description",
                "idx_followers_count",
                "idx_location",
                "idx_login",
                "idx_name",
                "idx_public_repositories_count",
                "idx_url",
            ]

        case _:
            params["attributesToRetrieve"] = []

    return params
