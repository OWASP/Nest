"""OWASP app chapter index."""

from apps.common.index import IndexBase, register
from apps.owasp.models.chapter import Chapter


@register(Chapter)
class ChapterIndex(IndexBase):
    """Chapter index."""

    index_name = "chapters"

    fields = (
        "idx_country",
        "idx_created_at",
        "idx_is_active",
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
    )

    geo_field = "idx_geo_location"

    settings = {
        "attributesForFaceting": [
            "filterOnly(idx_is_active)",
            "filterOnly(idx_key)",
            "idx_country",
            "idx_name",
            "idx_tags",
        ],
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
            "unordered(idx_top_contributors.login, idx_top_contributors.name)",
            "unordered(idx_suggested_location, idx_country, idx_region, idx_postal_code)",
            "unordered(idx_tags)",
        ],
    }

    should_index = "is_indexable"

    def get_entities(self):
        """Get entities for indexing."""
        return Chapter.active_chapters.select_related(
            "owasp_repository",
        )
