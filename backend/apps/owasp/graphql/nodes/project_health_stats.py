"""OWASP Project Health Stats Node."""

import strawberry


@strawberry.type
class ProjectHealthStatsNode:
    """Node representing overall health stats of OWASP projects."""

    average_score: float
    monthly_overall_scores: list[float]
    projects_count_healthy: int
    projects_count_need_attention: int
    projects_count_unhealthy: int
    projects_percentage_healthy: float
    projects_percentage_need_attention: float
    projects_percentage_unhealthy: float
    total_contributors: int
    total_forks: int
    total_stars: int
