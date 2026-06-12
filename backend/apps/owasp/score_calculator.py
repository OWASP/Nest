"""Contribution score calculation service."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db.models import Q

from apps.github.models.issue import Issue
from apps.github.models.pull_request import PullRequest
from apps.github.models.user import User
from apps.owasp.models.crp.contribution_score import ContributionScore
from apps.owasp.models.crp.scoring_weight import ScoringWeight

if TYPE_CHECKING:
    from datetime import date


logger: logging.Logger = logging.getLogger(__name__)


class ContributionScoreCalculator:
    """Service for calculating contributor scores and assigning tiers."""

    BATCH_SIZE = 100

    def __init__(self):
        """Initialize the calculator and load scoring weights."""
        self.scoring_weights = self.load_scoring_weights()

    def load_scoring_weights(self) -> dict[str, int]:
        """Load active scoring weights from database.

        Returns:
            dict[str, int]: Dict mapping event types to scores.

        """
        return {
            weight.event_type: weight.score
            for weight in ScoringWeight.objects.filter(is_active=True)
        }

    def calculate_score(
        self,
        user: User,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> tuple[int, dict[str, int]]:
        """Calculate contribution score for a user.

        Args:
            user (User): The user to calculate score for.
            start_date (date, optional): Start date for filtering contributions.
            end_date (date, optional): End date for filtering contributions.

        Returns:
            tuple[int, dict[str, int]]: Total score and contribution breakdown.

        """
        breakdown = self.get_contribution_breakdown(user, start_date, end_date)
        total_score = sum(breakdown.values())

        return total_score, breakdown

    def get_contribution_breakdown(
        self,
        user: User,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict[str, int]:
        """Get score breakdown by contribution type.

        Args:
            user (User): The user to calculate for.
            start_date (date, optional): Start date filter.
            end_date (date, optional): End date filter.

        Returns:
            dict[str, int]: Score breakdown by event type.

        """
        breakdown: dict[str, int] = {}

        # Count merged PRs
        pr_merged_count = self.count_merged_pull_requests(user, start_date, end_date)
        breakdown["pr_merged"] = pr_merged_count * self.scoring_weights.get("pr_merged", 0)

        # Count opened PRs
        pr_opened_count = self.count_opened_pull_requests(user, start_date, end_date)
        breakdown["pr_opened"] = pr_opened_count * self.scoring_weights.get("pr_opened", 0)

        # Count opened issues
        issue_opened_count = self.count_opened_issues(user, start_date, end_date)
        breakdown["issue_opened"] = issue_opened_count * self.scoring_weights.get(
            "issue_opened", 0
        )

        return breakdown

    def count_merged_pull_requests(
        self,
        user: User,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> int:
        """Count merged PRs created by user.

        Args:
            user (User): The user.
            start_date (date, optional): Start date filter.
            end_date (date, optional): End date filter.

        Returns:
            int: Count of merged PRs.

        """
        query = PullRequest.objects.filter(
            author=user,
            merged_at__isnull=False,
            repository__is_fork=False,
            repository__organization__is_owasp_related_organization=True,
        )

        if start_date:
            query = query.filter(merged_at__date__gte=start_date)
        if end_date:
            query = query.filter(merged_at__date__lte=end_date)

        return query.count()

    def count_opened_pull_requests(
        self,
        user: User,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> int:
        """Count opened PRs created by user.

        Args:
            user (User): The user.
            start_date (date, optional): Start date filter.
            end_date (date, optional): End date filter.

        Returns:
            int: Count of opened PRs.

        """
        query = PullRequest.objects.filter(
            author=user,
            repository__is_fork=False,
            repository__organization__is_owasp_related_organization=True,
        )

        if start_date:
            query = query.filter(created_at__date__gte=start_date)
        if end_date:
            query = query.filter(created_at__date__lte=end_date)

        return query.count()

    def count_opened_issues(
        self,
        user: User,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> int:
        """Count opened issues created by user."""
        query = Issue.objects.filter(
            author=user,
            state_reason=Issue.StateReason.COMPLETED,
            repository__is_fork=False,
            repository__organization__is_owasp_related_organization=True,
        )

        if start_date:
            query = query.filter(created_at__date__gte=start_date)
        if end_date:
            query = query.filter(created_at__date__lte=end_date)

        return query.count()

    def get_tier(self, score: int) -> str:
        """Determine contributor tier based on score.

        Args:
            score (int): The contributor's total score.

        Returns:
            str: The tier level.

        """
        # Tier thresholds mapped to tier values
        tiers_by_score = [
            ("level_4", 500),
            ("level_3", 250),
            ("level_2", 100),
            ("level_1", 0),
        ]

        for tier_value, threshold in tiers_by_score:
            if score >= threshold:
                return tier_value

        return "level_1"

    def recalculate_all_scores(self) -> dict[str, int]:
        """Recalculate scores for all users.

        Returns:
            dict: Statistics about the recalculation.

        """
        # Get all indexed users with contributions
        pr_authors = PullRequest.objects.filter(
            repository__is_fork=False,
            repository__organization__is_owasp_related_organization=True,
        ).values("author_id")

        issue_authors = Issue.objects.filter(
            state_reason=Issue.StateReason.COMPLETED,
            repository__is_fork=False,
            repository__organization__is_owasp_related_organization=True,
        ).values("author_id")

        users_with_contributions = User.objects.filter(
            Q(id__in=pr_authors) | Q(id__in=issue_authors),
        ).distinct()

        total_users = users_with_contributions.count()
        updated_count = 0
        created_count = 0

        logger.info("Starting score recalculation for %s users", total_users)

        contribution_scores = []

        for user in users_with_contributions:
            total_score, _ = self.calculate_score(user)
            tier = self.get_tier(total_score)

            try:
                score = user.contribution_score
                score.value = total_score
                score.tier = tier
                contribution_scores.append(score)
                updated_count += 1

            except ContributionScore.DoesNotExist:
                score = ContributionScore(
                    github_user=user,
                    value=total_score,
                    tier=tier,
                )
                contribution_scores.append(score)
                created_count += 1

            if len(contribution_scores) >= self.BATCH_SIZE:
                ContributionScore.bulk_save(
                    ContributionScore, contribution_scores, fields=("value", "tier")
                )

        if contribution_scores:
            ContributionScore.bulk_save(
                ContributionScore, contribution_scores, fields=("value", "tier")
            )

        logger.info(
            "Score recalculation complete. Created: %s, Updated: %s",
            created_count,
            updated_count,
        )

        return {
            "total": total_users,
            "created": created_count,
            "updated": updated_count,
        }

    def recalculate_user_score(self, user: User) -> dict[str, str | int | bool]:
        """Recalculate score for a single user.

        Args:
            user (User): The user to recalculate.

        Returns:
            dict[str, str | int | bool]: The updated score, tier, and creation flag.

        """
        total_score, _ = self.calculate_score(user)
        tier = self.get_tier(total_score)

        _, created = ContributionScore.objects.update_or_create(
            github_user=user,
            defaults={
                "value": total_score,
                "tier": tier,
            },
        )

        logger.info(
            "Recalculated score for %s: %s points (%s)",
            user.login,
            total_score,
            tier,
        )

        return {
            "total_score": total_score,
            "tier": tier,
            "created": created,
        }
