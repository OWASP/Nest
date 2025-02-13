"""OWASP committee GraphQL node."""

import graphene

from apps.owasp.graphql.nodes.common import GenericEntityNode
from apps.owasp.models.committee import Committee


class CommitteeNode(GenericEntityNode):
    """Committee node."""

    contributors_count = graphene.Int()
    created_at = graphene.Float()
    forks_count = graphene.Int()
    issues_count = graphene.Int()
    repositories_count = graphene.Int()
    stars_count = graphene.Int()

    class Meta:
        model = Committee
        fields = (
            "name",
            "summary",
        )

    def resolve_created_at(self, info):
        """Resolve created at."""
        return self.idx_created_at

    def resolve_contributors_count(self, info):
        """Resolve contributors count."""
        return self.owasp_repository.contributors_count

    def resolve_forks_count(self, info):
        """Resolve forks count."""
        return self.owasp_repository.forks_count

    def resolve_issues_count(self, info):
        """Resolve issues count."""
        return self.owasp_repository.open_issues_count

    def resolve_repositories_count(self, info):
        """Resolve repositories count."""
        return 1

    def resolve_stars_count(self, info):
        """Resolve stars count."""
        return self.owasp_repository.stars_count
