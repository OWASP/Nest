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
        "idx_meetup_group",
        "idx_name",
        "idx_postal_code",
        "idx_region",
        "idx_tags",
    )

    geo_field = "idx_geo_location"

    settings = {
        "indexLanguages": ["en"],
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
            "unordered(idx_country, idx_region, idx_postal_code)",
            "unordered(idx_tags)",
        ],
    }

    should_index = "is_indexable"

    def get_queryset(self):
        """Get queryset."""
        return Chapter.objects.prefetch_related(
            "owasp_repository",
        )
