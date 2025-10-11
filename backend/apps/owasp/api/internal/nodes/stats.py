"""OWASP stats GraphQL node."""

import strawberry


@strawberry.type
class StatsNode:
    """Stats node."""

    active_chapters_stats: int
    active_projects_stats: int
    contributors_stats: int
    countries_stats: int
    slack_workspace_stats: int
