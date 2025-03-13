"""GraphQL schema."""

from collections import defaultdict

import graphene

from apps.github.graphql.queries import GithubQuery
from apps.owasp.graphql.queries import OwaspQuery


class Query(GithubQuery, OwaspQuery):
    """Schema queries."""

    recent_issues_releases = graphene.List(
        graphene.String,
        distinct=graphene.Boolean(default_value=False),
        description="Fetch recent issues/releases with optional distinct parameter",
    )

    def resolve_recent_issues_releases(self, info, distinct):
        """Resolve recent issues releases.

        Args:
        ----
            info: GraphQL execution info.
            distinct (bool): Whether to return distinct issues releases.

        Returns:
        -------
            list: A list of recent issues releases.

        """
        # Mock data
        issues_releases = [
            {"author": "author1", "project": "project1", "title": "Issue 1"},
            {"author": "author1", "project": "project1", "title": "Issue 2"},
            {"author": "author2", "project": "project2", "title": "Release 1"},
            {"author": "author2", "project": "project2", "title": "Release 2"},
        ]

        if distinct:
            unique_entries = defaultdict(list)
            for entry in issues_releases:
                key = (entry["author"], entry["project"])
                if key not in unique_entries:
                    unique_entries[key].append(entry)
            issues_releases = [item for sublist in unique_entries.values() for item in sublist]

        return [issue_release["title"] for issue_release in issues_releases]


schema = graphene.Schema(query=Query)
