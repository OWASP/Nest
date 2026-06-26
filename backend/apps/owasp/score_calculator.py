"""Contribution score calculation service."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.db.models import Count, Q

from apps.common.models import BulkSaveModel
from apps.github.models.issue import Issue
from apps.github.models.pull_request import PullRequest
from apps.github.models.user import User
from apps.owasp.exceptions import CertificateIssuanceError
from apps.owasp.models.crp.contribution_score import ContributionScore
from apps.owasp.models.crp.recognition_enums import TierChoices
from apps.owasp.models.crp.scoring_weight import ScoringWeight
from apps.owasp.services.certificate_service import CertificateService

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

    def calculate(
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

    def calculate_score(self, counts: dict[str, int]) -> tuple[int, dict[str, int]]:
        """Calculate total score and breakdown from contribution counts."""
        breakdown = {
            event_type: count * self.scoring_weights.get(event_type, 0)
            for event_type, count in counts.items()
        }
        return sum(breakdown.values()), breakdown

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
        counts = {
            "pr_merged": self.count_merged_pull_requests(user, start_date, end_date),
            "pr_opened": self.count_opened_pull_requests(user, start_date, end_date),
            "issue_opened": self.count_opened_issues(user, start_date, end_date),
        }
        _, breakdown = self.calculate_score(counts)
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

    def get_tier(self, score: int) -> TierChoices:
        """Determine contributor tier based on score.

        Args:
            score (int): The contributor's total score.

        Returns:
            TierChoices: The tier level choice.

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
                return TierChoices(tier_value)

        return TierChoices("level_1")

    def recalculate_all(self) -> dict[str, Any]:
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

        users_with_contributions = (
            User.objects.filter(
                Q(id__in=pr_authors) | Q(id__in=issue_authors),
            )
            .distinct()
            .prefetch_related("contribution_score")
        )

        total_users = users_with_contributions.count()
        updated_count = 0
        created_count = 0

        logger.info("Starting score recalculation for %s users", total_users)

        pr_merged_counts: dict[int, int] = dict(
            PullRequest.objects.filter(
                merged_at__isnull=False,
                repository__is_fork=False,
                repository__organization__is_owasp_related_organization=True,
            )
            .values("author_id")
            .annotate(count=Count("id"))
            .values_list("author_id", "count")
        )

        pr_opened_counts: dict[int, int] = dict(
            PullRequest.objects.filter(
                repository__is_fork=False,
                repository__organization__is_owasp_related_organization=True,
            )
            .values("author_id")
            .annotate(count=Count("id"))
            .values_list("author_id", "count")
        )

        issue_opened_counts: dict[int, int] = dict(
            Issue.objects.filter(
                state_reason=Issue.StateReason.COMPLETED,
                repository__is_fork=False,
                repository__organization__is_owasp_related_organization=True,
            )
            .values("author_id")
            .annotate(count=Count("id"))
            .values_list("author_id", "count")
        )

        contribution_scores = []
        pending_certificates = []
        failed_certificates: list[tuple[str, Exception]] = []

        for user in users_with_contributions:
            counts = {
                "pr_merged": pr_merged_counts.get(user.id, 0),
                "pr_opened": pr_opened_counts.get(user.id, 0),
                "issue_opened": issue_opened_counts.get(user.id, 0),
            }
            total_score, _ = self.calculate_score(counts)
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

            pending_certificates.append(score)

            if len(contribution_scores) >= self.BATCH_SIZE:
                BulkSaveModel.bulk_save(
                    ContributionScore, contribution_scores, fields=["value", "tier"]
                )
                for pending_score in pending_certificates:
                    try:
                        CertificateService.issue_certificate(
                            pending_score.github_user,
                            pending_score.value,
                            TierChoices(pending_score.tier),
                        )
                    except CertificateIssuanceError as e:
                        logger.exception(
                            "Failed to issue certificate for user %s",
                            pending_score.github_user.login,
                        )
                        failed_certificates.append((pending_score.github_user.login, e))
                    except Exception as e:
                        logger.exception(
                            "Unexpected certificate processing error for user %s",
                            pending_score.github_user.login,
                        )
                        failed_certificates.append((pending_score.github_user.login, e))
                pending_certificates.clear()
                contribution_scores.clear()

        if contribution_scores:
            BulkSaveModel.bulk_save(
                ContributionScore, contribution_scores, fields=["value", "tier"]
            )
            for pending_score in pending_certificates:
                try:
                    CertificateService.issue_certificate(
                        pending_score.github_user,
                        pending_score.value,
                        TierChoices(pending_score.tier),
                    )
                except CertificateIssuanceError as e:
                    logger.exception(
                        "Failed to issue certificate for user %s",
                        pending_score.github_user.login,
                    )
                    failed_certificates.append((pending_score.github_user.login, e))
            pending_certificates.clear()
            contribution_scores.clear()

        logger.info(
            "Score recalculation complete. Created: %s, Updated: %s",
            created_count,
            updated_count,
        )

        return {
            "total": total_users,
            "created": created_count,
            "updated": updated_count,
            "failed_count": len(failed_certificates),
            "failures": failed_certificates,
        }

    def recalculate_user(self, user: User) -> dict[str, str | int | bool]:
        """Recalculate score for a single user.

        Args:
            user (User): The user to recalculate.

        Returns:
            dict[str, str | int | bool]: The updated score, tier, and creation flag.

        """
        total_score, _ = self.calculate(user)
        tier = self.get_tier(total_score)

        _, created = ContributionScore.objects.update_or_create(
            github_user=user,
            defaults={
                "value": total_score,
                "tier": tier,
            },
        )

        CertificateService.issue_certificate(user, total_score, tier)

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
