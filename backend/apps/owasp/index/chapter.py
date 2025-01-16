"""OWASP app chapter index."""

from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from apps.common.index import IS_LOCAL_BUILD, LOCAL_INDEX_LIMIT
from apps.owasp.models.chapter import Chapter


@register(Chapter)
class ChapterIndex(AlgoliaIndex):
    """Chapter index."""

    index_name = "chapters"

    fields = (
        "idx_country",
        "idx_created_at",
        "idx_key",
        "idx_leaders",
        "idx_name",
        "idx_postal_code",
        "idx_region",
        "idx_related_urls",
        "idx_suggested_location",
        "idx_top_contributors",
        "idx_summary",
        "idx_tags",
        "idx_updated_at",
        "idx_url",
        "idx_is_active",
    )

    geo_field = "idx_geo_location"

    settings = {
        "attributesForFaceting": [
            "filterOnly(idx_key)",
            "idx_country",
            "idx_name",
            "idx_tags",
        ],
        "indexLanguages": ["en"],
        "customRanking": [
            "desc(idx_is_active)",
            "asc(idx_created_at)",
            "desc(idx_updated_at)",
        ],
        "ranking": [
            "typo",
            "geo",
            "words",
            "filters",
            "proximity",
            "attribute",
            "exact",
            "custom",
        ],
        "searchableAttributes": [
            "unordered(idx_name)",
            "unordered(idx_leaders)",
            "unordered(idx_top_contributors.login, idx_top_contributors.name)",
            "unordered(idx_suggested_location, idx_country, idx_region, idx_postal_code)",
            "unordered(idx_tags)",
        ],
    }

    should_index = "is_indexable"

    def get_queryset(self):
        """Get queryset."""
        qs = Chapter.active_chapters.select_related(
            "owasp_repository",
        )
        return qs[:LOCAL_INDEX_LIMIT] if IS_LOCAL_BUILD else qs
