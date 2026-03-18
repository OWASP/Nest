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
        "idx_is_owasp_staff",
        "idx_owasp_board_member",
        "idx_owasp_gsoc_mentor",
        "idx_has_project_affinity",
        "idx_has_chapter_affinity",
        "idx_has_committee_affinity",
    )

    settings = {
        "attributesForFaceting": [
            "idx_key",
            "idx_name",
            "idx_title",
            "idx_is_owasp_staff",
            "idx_owasp_board_member",
            "idx_owasp_gsoc_mentor",
            "idx_has_project_affinity",
            "idx_has_chapter_affinity",
            "idx_has_committee_affinity",
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
    def configure_replicas() -> None:  # type: ignore[override]
        """Configure the settings for user replicas."""
        replicas = {
            "contributions_count_asc": ["asc(idx_contributions_count)"],
            "contributions_count_desc": ["desc(idx_contributions_count)"],
            "followers_count_asc": ["asc(idx_followers_count)"],
            "followers_count_desc": ["desc(idx_followers_count)"],
            "public_repositories_count_asc": ["asc(idx_public_repositories_count)"],
            "public_repositories_count_desc": ["desc(idx_public_repositories_count)"],
        }

        base_settings = {
            "attributesForFaceting": [
                "idx_key",
                "idx_name",
                "idx_title",
                "idx_is_owasp_staff",
                "idx_owasp_board_member",
                "idx_owasp_gsoc_mentor",
                "idx_has_project_affinity",
                "idx_has_chapter_affinity",
                "idx_has_committee_affinity",
            ]
        }

        IndexBase.configure_replicas("users", replicas, base_settings)

    @staticmethod
    def update_synonyms() -> None:
        """Update synonyms for the user index."""
        UserIndex.reindex_synonyms("github", "users")

    def get_entities(self) -> QuerySet:
        """Get entities for indexing.

        Returns:
            QuerySet: A queryset of User objects to be indexed.

        """
        return (
            User.objects.exclude(
                Q(is_bot=True) | Q(login__in=User.get_non_indexable_logins()),
            )
            .select_related("owasp_profile")
            .prefetch_related("chapters", "projects")
        )
