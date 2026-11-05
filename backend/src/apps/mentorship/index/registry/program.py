"""OWASP app program index."""

from apps.common.index import IndexBase, register
from apps.mentorship.models import Program


@register(Program)
class ProgramIndex(IndexBase):
    """Program index."""

    index_name = "programs"

    fields = (
        "idx_description",
        "idx_ended_at",
        "idx_experience_levels",
        "idx_key",
        "idx_name",
        "idx_started_at",
        "idx_status",
    )

    settings = {
        "attributesForFaceting": [
            "filterOnly(idx_status)",
            "idx_experience_levels",
        ],
        "indexLanguages": ["en"],
        "customRanking": [],
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
            "unordered(idx_description)",
            "unordered(idx_experience_levels)",
            "unordered(idx_name)",
        ],
    }

    should_index = "is_indexable"

    def get_entities(self):
        """Return only published programs for indexing."""
        return Program.objects.filter(status=Program.ProgramStatus.PUBLISHED)
