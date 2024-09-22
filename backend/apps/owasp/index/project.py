"""OWASP app project index."""

from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from apps.owasp.models.project import Project


@register(Project)
class ProjectIndex(AlgoliaIndex):
    """Project index."""

    index_name = "projects"

    fields = (
        "idx_companies",
        "idx_top_contributors",
        "idx_contributors_count",
        "idx_description",
        "idx_forks_count",
        "idx_languages",
        "idx_leaders",
        "idx_level",
        "idx_level_raw",
        "idx_name",
        "idx_organizations",
        "idx_stars_count",
        "idx_summary",
        "idx_tags",
        "idx_topics",
        "idx_type",
        "idx_updated_at",
        "idx_url",
    )

    settings = {
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
            "unordered(idx_languages, idx_tags, idx_topics)",
            "unordered(idx_description)",
            "unordered(idx_companies, idx_organizations)",
            "unordered(idx_leaders, idx_top_contributors.login, idx_top_contributors.name)",
            "unordered(idx_level)",
        ],
    }

    should_index = "is_indexable"

    def get_queryset(self):
        """Get queryset."""
        return Project.objects.prefetch_related(
            "organizations",
            "repositories",
        )