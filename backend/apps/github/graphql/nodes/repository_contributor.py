"""GitHub repository GraphQL node."""

import strawberry


@strawberry.type
class RepositoryContributorNode:
    """Repository contributor node."""

    avatar_url: str
    contributions_count: int
    login: str
    name: str
    project_key: str
    project_name: str
