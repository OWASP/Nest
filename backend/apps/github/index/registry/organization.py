"""GitHub OWASP related organizations Algolia index configuration."""

from django.db.models import QuerySet

from apps.common.index import IndexBase, register
from apps.github.models.organization import Organization


@register(Organization)
class OrganizationIndex(IndexBase):
    """Organization index."""

    index_name = "organizations"

    fields = (
        "idx_avatar_url",
        "idx_collaborators_count",
        "idx_created_at",
        "idx_description",
        "idx_followers_count",
        "idx_location",
        "idx_login",
        "idx_name",
        "idx_public_repositories_count",
        "idx_url",
    )

    settings = {
        "minProximity": 4,
        "customRanking": [
            "desc(idx_followers_count)",
            "desc(idx_collaborators_count)",
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
            "unordered(idx_name)",
            "unordered(idx_login)",
        ],
    }

    should_index = "is_indexable"

    @staticmethod
    def update_synonyms() -> None:
        """Update synonyms for the organizations index."""
        OrganizationIndex.reindex_synonyms("github", "organizations")

    def get_entities(self) -> QuerySet:
        """Get the queryset of Organization objects to be indexed.

        Returns:
          QuerySet: A queryset of Organization objects.

        """
        return Organization.objects.filter(is_owasp_related_organization=True)
