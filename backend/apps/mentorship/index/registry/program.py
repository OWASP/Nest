"""OWASP app program index."""

from apps.common.index import IndexBase, register
from apps.mentorship.models.program import Program


@register(Program)
class ProgramIndex(IndexBase):
    """Program index."""

    index_name = "programs"

    fields = (
        "idx_name",
        "idx_key",
        "idx_status",
        "idx_description",
        "idx_experience_levels",
        "idx_admins",
        "idx_started_at",
        "idx_ended_at",
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
            "unordered(idx_name)",
            "unordered(idx_description)",
            "unordered(idx_experience_levels)",
            "unordered(idx_admins.login)",
            "unordered(idx_admins.name)",
        ],
    }

    should_index = "is_indexable"

    def get_entities(self):
        """Return only published programs for indexing."""
        return Program.objects.filter(status=Program.ProgramStatus.PUBLISHED)
