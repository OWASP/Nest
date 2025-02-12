"""OWASP app project index."""

from apps.common.index import IndexBase, register
from apps.owasp.models.project import Project


@register(Project)
class ProjectIndex(IndexBase):
    """Project index."""

    index_name = "projects"

    fields = (
        "idx_companies",
        "idx_contributors_count",
        "idx_custom_tags",
        "idx_description",
        "idx_forks_count",
        "idx_issues_count",
        "idx_is_active",
        "idx_key",
        "idx_languages",
        "idx_leaders",
        "idx_level_raw",
        "idx_level",
        "idx_name",
        "idx_organizations",
        "idx_repositories",
        "idx_repositories_count",
        "idx_stars_count",
        "idx_summary",
        "idx_tags",
        "idx_top_contributors",
        "idx_topics",
        "idx_type",
        "idx_updated_at",
        "idx_url",
    )

    settings = {
        "attributesForFaceting": [
            "filterOnly(idx_is_active)",
            "filterOnly(idx_key)",
            "idx_name",
            "idx_tags",
            "idx_repositories.name",
        ],
        "indexLanguages": ["en"],
        "customRanking": [
            "desc(idx_level_raw)",
            "desc(idx_stars_count)",
            "desc(idx_contributors_count)",
            "desc(idx_forks_count)",
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
            "unordered(idx_repositories.description, idx_repositories.name)",
            "unordered(idx_custom_tags, idx_languages, idx_tags, idx_topics)",
            "unordered(idx_description)",
            "unordered(idx_companies, idx_organizations)",
            "unordered(idx_leaders)",
            "unordered(idx_top_contributors.login, idx_top_contributors.name)",
            "unordered(idx_level)",
        ],
    }

    should_index = "is_indexable"

    @staticmethod
    def configure_replicas():
        """Configure the settings for project replicas."""
        replicas = {
            "contributors_count_asc": ["asc(idx_contributors_count)"],
            "contributors_count_desc": ["desc(idx_contributors_count)"],
            "forks_count_asc": ["asc(idx_forks_count)"],
            "forks_count_desc": ["desc(idx_forks_count)"],
            "name_asc": ["asc(idx_name)"],
            "name_desc": ["desc(idx_name)"],
            "stars_count_asc": ["asc(idx_stars_count)"],
            "stars_count_desc": ["desc(idx_stars_count)"],
        }

        IndexBase.configure_replicas("projects", replicas)

    @staticmethod
    def update_synonyms():
        """Update synonyms."""
        return IndexBase.reindex_synonyms("owasp", "projects")

    def get_entities(self):
        """Get entities for indexing."""
        return Project.objects.prefetch_related(
            "organizations",
            "repositories",
        )
