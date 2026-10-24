"""OWASP app program index."""

from apps.common.index import IndexBase, register
from apps.mentorship.models import Program


@register(Program)
class ProgramIndex(IndexBase):
    """Program index."""

    index_name = "programs"

    fields = (
        "idx_created_at",
        "idx_description",
        "idx_ended_at",
        "idx_experience_levels",
        "idx_key",
        "idx_name",
        "idx_started_at",
        "idx_status",
        "idx_updated_at",
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

    @staticmethod
    def configure_replicas() -> None:  # type: ignore[override]
        """Configure the settings for program replicas."""
        replicas = {
            "name_asc": ["asc(idx_name)"],
            "name_desc": ["desc(idx_name)"],
            "created_at_asc": ["asc(idx_created_at)"],
            "created_at_desc": ["desc(idx_created_at)"],
            "updated_at_asc": ["asc(idx_updated_at)"],
            "updated_at_desc": ["desc(idx_updated_at)"],
            "ended_at_asc": ["asc(idx_ended_at)"],
            "ended_at_desc": ["desc(idx_ended_at)"],
        }

        IndexBase.configure_replicas("programs", replicas)

    def get_entities(self):
        """Return only published programs for indexing."""
        return Program.objects.filter(status=Program.ProgramStatus.PUBLISHED)
