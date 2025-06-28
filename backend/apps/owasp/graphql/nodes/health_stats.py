"""OWASP Project Health Stats Node."""

import strawberry


@strawberry.type
class HealthStatsNode:
    """Node representing overall health stats of OWASP projects."""

    healthy_projects_count: int
    healthy_projects_percentage: float
    projects_needing_attention_count: int
    projects_needing_attention_percentage: float
    unhealthy_projects_count: int
    unhealthy_projects_percentage: float
    average_score: float
    total_stars: int
    total_forks: int
    total_contributors: int
    monthly_overall_scores: list[float]
