"""GitHub release Algolia index configuration."""

from algoliasearch_django import AlgoliaIndex

from apps.common.index import IS_LOCAL_BUILD, LOCAL_INDEX_LIMIT, IndexBase, conditional_register
from apps.github.models.release import Release


@conditional_register(Release)
class ReleaseIndex(AlgoliaIndex, IndexBase):
    """Release index."""

    index_name = "releases"

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
        qs = Release.objects.filter(
            is_draft=False,
            published_at__isnull=False,
        )
        return qs[:LOCAL_INDEX_LIMIT] if IS_LOCAL_BUILD else qs

    @staticmethod
    def update_synonyms():
        """Update synonyms."""
        ReleaseIndex.reindex_synonyms("github", "releases")
