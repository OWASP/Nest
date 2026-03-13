"""Member score calculation service.

Computes a composite ranking score for OWASP community members
based on multiple weighted factors.
"""

from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

WEIGHT_CONTRIBUTIONS = 0.30
WEIGHT_LEADERSHIP = 0.25
WEIGHT_RECENCY = 0.20
WEIGHT_BREADTH = 0.10
WEIGHT_TYPE_DIVERSITY = 0.10
WEIGHT_CONSISTENCY = 0.05

POINTS_PROJECT_LEADER = 20
POINTS_CHAPTER_LEADER = 15
POINTS_COMMITTEE_MEMBER = 10
POINTS_BOARD_MEMBER = 30
POINTS_GSOC_MENTOR = 15
POINTS_OWASP_STAFF = 10

MAX_PROJECT_LEADER_POINTS = 60
MAX_CHAPTER_LEADER_POINTS = 45
MAX_COMMITTEE_MEMBER_POINTS = 30

MAX_SCORE = 100


class MemberScoreCalculator:
    """Calculate composite ranking scores for OWASP community members."""

    def calculate(self, user) -> float:
        """Calculate the composite score for a user.

        Args:
            user: User instance with related data.

        Returns:
            float: Weighted composite score.

        """
        contribution = self._contribution_score(user)
        leadership = self._leadership_score(user)
        recency = self._recency_score(user)
        breadth = self._breadth_score(user)
        type_diversity = self._type_diversity_score(user)
        consistency = self._consistency_score(user)

        return round(
            WEIGHT_CONTRIBUTIONS * contribution
            + WEIGHT_LEADERSHIP * leadership
            + WEIGHT_RECENCY * recency
            + WEIGHT_BREADTH * breadth
            + WEIGHT_TYPE_DIVERSITY * type_diversity
            + WEIGHT_CONSISTENCY * consistency,
            2,
        )

    @staticmethod
    def _contribution_score(user) -> float:
        """Score based on total contribution count using logarithmic scaling.

        Args:
            user: User instance.

        Returns:
            float: Score from 0 to 100.

        """
        if user.contributions_count <= 0:
            return 0
        return min(MAX_SCORE, math.log2(1 + user.contributions_count) * 10)

    @staticmethod
    def _leadership_score(user) -> float:
        """Score based on community leadership roles.

        Args:
            user: User instance.

        Returns:
            float: Score from 0 to 100.

        """
        from apps.owasp.models.chapter import Chapter  # noqa: PLC0415
        from apps.owasp.models.committee import Committee  # noqa: PLC0415
        from apps.owasp.models.entity_member import EntityMember  # noqa: PLC0415
        from apps.owasp.models.project import Project  # noqa: PLC0415

        score = 0

        leader_memberships = EntityMember.objects.filter(
            member=user,
            is_active=True,
            is_reviewed=True,
        )

        project_ct = ContentType.objects.get_for_model(Project)
        chapter_ct = ContentType.objects.get_for_model(Chapter)
        committee_ct = ContentType.objects.get_for_model(Committee)

        project_leader_count = leader_memberships.filter(
            entity_type=project_ct,
            role=EntityMember.Role.LEADER,
        ).count()
        score += min(project_leader_count * POINTS_PROJECT_LEADER, MAX_PROJECT_LEADER_POINTS)

        chapter_leader_count = leader_memberships.filter(
            entity_type=chapter_ct,
            role=EntityMember.Role.LEADER,
        ).count()
        score += min(chapter_leader_count * POINTS_CHAPTER_LEADER, MAX_CHAPTER_LEADER_POINTS)

        committee_member_count = leader_memberships.filter(
            entity_type=committee_ct,
            role__in=[EntityMember.Role.LEADER, EntityMember.Role.MEMBER],
        ).count()
        score += min(committee_member_count * POINTS_COMMITTEE_MEMBER, MAX_COMMITTEE_MEMBER_POINTS)

        try:
            profile = user.owasp_profile
            if profile.is_owasp_board_member:
                score += POINTS_BOARD_MEMBER
            if profile.is_gsoc_mentor:
                score += POINTS_GSOC_MENTOR
        except ObjectDoesNotExist:
            pass

        if user.is_owasp_staff:
            score += POINTS_OWASP_STAFF

        return min(score, MAX_SCORE)

    @staticmethod
    def _recency_score(user) -> float:
        """Score based on recent contribution activity.

        Contributions are weighted by recency:
        - Last 90 days: weight 3x
        - 91-180 days: weight 2x
        - 181-365 days: weight 1x

        Args:
            user: User instance.

        Returns:
            float: Score from 0 to 100.

        """
        contribution_data = user.contribution_data
        if not contribution_data:
            return 0

        now = datetime.now(tz=UTC).date()
        window_90 = now - timedelta(days=90)
        window_180 = now - timedelta(days=180)
        window_365 = now - timedelta(days=365)

        recent_90 = 0
        recent_180 = 0
        recent_365 = 0

        for date_str, count in contribution_data.items():
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC).date()
            except (ValueError, TypeError):
                continue

            if date >= window_90:
                recent_90 += count
            elif date >= window_180:
                recent_180 += count
            elif date >= window_365:
                recent_365 += count

        weighted_sum = recent_90 * 3 + recent_180 * 2 + recent_365 * 1

        if weighted_sum <= 0:
            return 0

        return min(MAX_SCORE, math.log2(1 + weighted_sum) * 8)

    @staticmethod
    def _breadth_score(user) -> float:
        """Score based on the number of distinct repositories contributed to.

        Args:
            user: User instance.

        Returns:
            float: Score from 0 to 100.

        """
        from apps.github.models.repository_contributor import (  # noqa: PLC0415
            RepositoryContributor,
        )

        distinct_repos = (
            RepositoryContributor.objects.filter(user=user)
            .exclude(
                Q(repository__is_fork=True)
                | Q(repository__organization__is_owasp_related_organization=False)
            )
            .values("repository")
            .distinct()
            .count()
        )

        return min(MAX_SCORE, distinct_repos * 10)

    @staticmethod
    def _type_diversity_score(user) -> float:
        """Score based on diversity of contribution types.

        Awards 25 points each for having: commits, PRs, issues, releases.

        Args:
            user: User instance.

        Returns:
            float: Score from 0 to 100.

        """
        from apps.github.models.repository_contributor import (  # noqa: PLC0415
            RepositoryContributor,
        )

        score = 0

        has_contributions = (
            RepositoryContributor.objects.filter(user=user, contributions_count__gt=0)
            .exclude(
                Q(repository__is_fork=True)
                | Q(repository__organization__is_owasp_related_organization=False)
            )
            .exists()
        )
        if has_contributions:
            score += 25

        if user.created_pull_requests.exists():
            score += 25

        if user.created_issues.exists():
            score += 25

        if user.created_releases.exists():
            score += 25

        return score

    @staticmethod
    def _consistency_score(user) -> float:
        """Score based on regularity of activity.

        Calculates the ratio of active days to total days in the
        contribution data period.

        Args:
            user: User instance.

        Returns:
            float: Score from 0 to 100.

        """
        contribution_data = user.contribution_data
        if not contribution_data:
            return 0

        total_days = len(contribution_data)
        if total_days == 0:
            return 0

        active_days = sum(1 for count in contribution_data.values() if count > 0)

        return min(MAX_SCORE, (active_days / total_days) * MAX_SCORE)
