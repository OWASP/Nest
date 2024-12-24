"""GitHub user index."""

from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register
from apps.common.index import IndexSynonymsMixin
from apps.github.models import User


@register(User)
class UserIndex(AlgoliaIndex, IndexSynonymsMixin):
    """User index for OWASP GitHub organization members."""

    index_name = "users"

    fields = (
        "idx_login",
        "idx_name",
        "idx_bio",
        "idx_avatar_url",
        "idx_company",
        "idx_location",
        "idx_email",
        "idx_public_repositories_count",
        "idx_followers_count",
        "idx_following_count",
        "idx_created_at",
        "idx_updated_at",
        "idx_type",
        "idx_url",
        "idx_title",
    )

    settings = {
        "attributeForDistinct": "idx_login",
        "minProximity": 4,
        "indexLanguages": ["en"],
        "customRanking": [
            "desc(idx_public_repositories_count)",
            "desc(idx_followers_count)",
            "desc(idx_created_at)",
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
            "unordered(idx_login, idx_name)",
            "unordered(idx_bio)",
            "unordered(idx_company, idx_location)",
            "unordered(idx_email)",
        ],
    }

    should_index = "is_indexable"

    def get_queryset(self):
        """Get queryset for indexing."""
        return User.objects.filter(type="User").select_related()

    @staticmethod
    def update_synonyms():
        """Update synonyms."""
        UserIndex.reindex_synonyms("github", "users")