"""OWASP app index."""

from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from apps.owasp.models.project import Project


@register(Project)
class ProjectIndex(AlgoliaIndex):
    """Project index."""

    index_name = "projects"

    fields = (
        "idx_contributors_count",
        "idx_description",
        "idx_forks_count",
        "idx_languages",
        "idx_leaders",
        "idx_level",
        "idx_name",
        "idx_organizations",
        "idx_companies",
        "idx_stars_count",
        "idx_tags",
        "idx_topics",
        "idx_updated_at",
    )

    settings = {
        "customRanking": [
            "desc(idx_level)",
            "desc(idx_stars_count)",
            "desc(idx_forks_count)",
            "desc(idx_contributors_count)",
        ],
        "searchableAttributes": [
            "idx_description",
            "idx_languages",
            "idx_leaders",
            "idx_name",
            "idx_organizations",
            "idx_companies",
            "idx_tags",
            "idx_topics",
        ],
    }

    should_index = "is_indexable"
