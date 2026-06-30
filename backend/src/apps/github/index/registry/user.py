"""GitHub user Algolia index configuration."""

from django.db.models import Q, QuerySet

from apps.common.index import IndexBase, register
from apps.github.models.user import User


@register(User)
class UserIndex(IndexBase):
    """User index."""

    index_name = "users"

    fields = (
        "idx_avatar_url",
        "idx_badge_count",
        "idx_bio",
        "idx_company",
        "idx_contributions",
        "idx_contributions_count",
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
            "desc(idx_contributions_count)",
            "desc(idx_followers_count)",
            "desc(idx_public_repositories_count)",
            "asc(idx_created_at)",
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
    def update_synonyms() -> None:
        """Update synonyms for the user index."""
        UserIndex.reindex_synonyms("github", "users")

    def get_entities(self) -> QuerySet:
        """Get entities for indexing.

        Returns:
            QuerySet: A queryset of User objects to be indexed.

        """
        return User.objects.exclude(
            Q(is_bot=True) | Q(login__in=User.get_non_indexable_logins()),
        )
