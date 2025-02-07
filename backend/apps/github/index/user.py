"""GitHub user Algolia index configuration."""

from apps.common.index import IndexBase, register
from apps.github.models.organization import Organization
from apps.github.models.user import User


@register(User)
class UserIndex(IndexBase):
    """User index."""

    index_name = "users"

    fields = (
        "idx_avatar_url",
        "idx_bio",
        "idx_company",
        "idx_contributions",
        "idx_created_at",
        "idx_email",
        "idx_followers_count",
        "idx_following_count",
        "idx_issues_count",
        "idx_key",
        "idx_location",
        "idx_login",
        "idx_name",
        "idx_public_repositories_count",
        "idx_title",
        "idx_updated_at",
        "idx_url",
    )

    settings = {
        "attributesForFaceting": [
            "idx_key",
            "idx_name",
            "idx_title",
        ],
        "attributeForDistinct": "idx_login",
        "minProximity": 4,
        "customRanking": [
            "desc(idx_created_at)",
            "desc(idx_followers_count)",
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
            "unordered(idx_email, idx_login, idx_name)",
            "unordered(idx_company, idx_location)",
            "unordered(idx_bio)",
        ],
    }

    should_index = "is_indexable"

    @staticmethod
    def update_synonyms():
        """Update synonyms."""
        UserIndex.reindex_synonyms("github", "users")

    def get_entities(self):
        """Get entities for indexing."""
        return User.objects.exclude(
            login__in=Organization.get_logins(),
        )
