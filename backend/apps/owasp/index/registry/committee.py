"""OWASP app chapter index."""

from apps.common.index import IndexBase, register
from apps.owasp.models.committee import Committee


@register(Committee)
class CommitteeIndex(IndexBase):
    """Committee index."""

    index_name = "committees"

    fields = (
        "idx_created_at",
        "idx_key",
        "idx_leaders",
        "idx_name",
        "idx_related_urls",
        "idx_top_contributors",
        "idx_summary",
        "idx_tags",
        "idx_updated_at",
        "idx_url",
    )

    settings = {
        "attributesForFaceting": [
            "filterOnly(idx_key)",
            "idx_name",
            "idx_tags",
        ],
        "indexLanguages": ["en"],
        "customRanking": [
            "asc(idx_name)",
            "asc(idx_created_at)",
            "desc(idx_updated_at)",
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
            "unordered(idx_name)",
            "unordered(idx_leaders)"
            "unordered(idx_top_contributors.login, idx_top_contributors.name)",
            "unordered(idx_tags)",
        ],
    }

    should_index = "is_indexable"

    def get_entities(self):
        """Get entities for indexing."""
        return Committee.active_committees.select_related(
            "owasp_repository",
        )
