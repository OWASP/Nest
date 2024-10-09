"""OWASP app chapter index."""

from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from apps.owasp.models.chapter import Chapter


@register(Chapter)
class ChapterIndex(AlgoliaIndex):
    """Chapter index."""

    index_name = "chapters"

    fields = (
        "idx_country",
        "idx_created_at",
        "idx_leaders",
        "idx_name",
        "idx_postal_code",
        "idx_region",
        "idx_related_urls",
        "idx_suggested_location",
        "idx_summary",
        "idx_tags",
        "idx_updated_at",
        "idx_url",
    )

    geo_field = "idx_geo_location"

    settings = {
        "indexLanguages": ["en"],
        "customRanking": [
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
            "unordered(idx_suggested_location, idx_country, idx_region, idx_postal_code)",
            "unordered(idx_tags)",
        ],
    }

    should_index = "is_indexable"

    def get_queryset(self):
        """Get queryset."""
        return Chapter.active_chapters.prefetch_related(
            "owasp_repository",
        )
