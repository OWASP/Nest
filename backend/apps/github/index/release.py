"""GitHub release Algolia index configuration."""

import os

from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from apps.common.constants import LOCAL_INDEX_LIMIT
from apps.common.index import IndexBase
from apps.github.models.release import Release


@register(Release)
class ReleaseIndex(AlgoliaIndex, IndexBase):
    """Release index."""

    index_name = "releaeses"

    fields = (
        "idx_author",
        "idx_created_at",
        "idx_description",
        "idx_name",
        "idx_project",
        "idx_published_at",
        "idx_repository",
        "idx_tag_name",
        "idx_is_pre_release",
    )

    settings = {
        "attributesForFaceting": [
            "filterOnly(idx_author)",
            "filterOnly(idx_project)",
            "filterOnly(idx_repository)",
        ],
        "minProximity": 4,
        "customRanking": [
            "desc(idx_published_at)",
            "desc(idx_created_at)",
        ],
        "ranking": [
            "typo",
            "words",
            "filters",
            "proximity",
            "attribute",
            "exact",
            "custom",
        ],
        "searchableAttributes": [
            "unordered(idx_name, idx_tag_name)",
            "unordered(idx_description)",
        ],
    }

    should_index = "is_indexable"

    def get_queryset(self):
        """Get queryset for indexing."""
        queryset = Release.objects.filter(
            is_draft=False,
            published_at__isnull=False,
        )
        if os.environ.get("DJANGO_CONFIGURATION", "Local") == "Local":
            return queryset[:LOCAL_INDEX_LIMIT]
        return queryset

    @staticmethod
    def update_synonyms():
        """Update synonyms."""
        ReleaseIndex.reindex_synonyms("github", "releases")
