"""OWASP Contribution Score GraphQL node."""

import strawberry_django

from apps.owasp.models.crp.contribution_score import ContributionScore


@strawberry_django.type(
    ContributionScore,
    fields=["value"],
)
class ContributionScoreNode:
    """Contribution score node."""
