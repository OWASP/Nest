"""GitHub repository Algolia index configuration."""

from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from apps.common.index import IndexBase
from apps.github.models.repository import Repository


@register(Repository)
class RepositoryIndex(AlgoliaIndex, IndexBase):
    """Repository index."""

    index_name = "repositories"

    fields = (
        "idx_commits_count",
        "idx_contributors_count",
        "idx_created_at",
        "idx_description",
        "idx_forks_count",
        "idx_has_funding_yml",
        "idx_key",
        "idx_languages",
        "idx_license",
        "idx_name",
        "idx_open_issues_count",
        "idx_project",
        "idx_pushed_at",
        "idx_size",
        "idx_stars_count",
        "idx_subscribers_count",
        "idx_top_contributors",
        "idx_topics",
        "idx_is_archived",
    )

    settings = {
        "minProximity": 4,
        "customRanking": [
            "asc(idx_is_archived)",
            "desc(idx_stars_count)",
            "desc(idx_forks_count)",
            "desc(idx_pushed_at)",
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
            "unordered(idx_description)",
            "unordered(idx_languages, idx_license, idx_topics)",
        ],
    }

    should_index = "is_indexable"

    def get_queryset(self):
        """Get queryset for indexing."""
        return Repository.objects.filter(is_template=False).prefetch_related(
            "repositorycontributor_set"
        )

    @staticmethod
    def update_synonyms():
        """Update synonyms."""
        RepositoryIndex.reindex_synonyms("github", "repositories")
