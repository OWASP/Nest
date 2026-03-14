"""Member score calculation service."""

from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta

WEIGHT_CONTRIBUTIONS = 0.25
WEIGHT_LEADERSHIP = 0.25
WEIGHT_RECENCY = 0.20
WEIGHT_BREADTH = 0.10
WEIGHT_TYPE_DIVERSITY = 0.10
WEIGHT_RELEASES = 0.05
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


def calculate_member_score(
    *,
    contributions_count: int,
    distinct_repository_count: int,
    release_count: int,
    chapter_leader_count: int,
    project_leader_count: int,
    committee_member_count: int,
    is_board_member: bool,
    is_gsoc_mentor: bool,
    is_owasp_staff: bool,
    has_pull_requests: bool,
    has_issues: bool,
    has_releases: bool,
    has_contributions: bool,
    contribution_data: dict | None,
) -> float:
    """Calculate the composite member ranking score.

    All inputs are simple values so this function is easy to test
    without database dependencies.

    Returns:
        float: The calculated ranking score (≥ 0).

    """
    contributions_score = _score_contributions(contributions_count)
    leadership_score = _score_leadership(
        chapter_leader_count=chapter_leader_count,
        project_leader_count=project_leader_count,
        committee_member_count=committee_member_count,
        is_board_member=is_board_member,
        is_gsoc_mentor=is_gsoc_mentor,
        is_owasp_staff=is_owasp_staff,
    )
    recency_score = _score_recency(contribution_data)
    breadth_score = _score_breadth(distinct_repository_count)
    type_diversity_score = _score_type_diversity(
        has_contributions=has_contributions,
        has_pull_requests=has_pull_requests,
        has_issues=has_issues,
        has_releases=has_releases,
    )
    releases_score = _score_releases(release_count)
    consistency_score = _score_consistency(contribution_data)

    total = (
        WEIGHT_CONTRIBUTIONS * contributions_score
        + WEIGHT_LEADERSHIP * leadership_score
        + WEIGHT_RECENCY * recency_score
        + WEIGHT_BREADTH * breadth_score
        + WEIGHT_TYPE_DIVERSITY * type_diversity_score
        + WEIGHT_RELEASES * releases_score
        + WEIGHT_CONSISTENCY * consistency_score
    )

    return round(total, 2)


def _score_contributions(contributions_count: int) -> float:
    """Score based on total contribution count using logarithmic scaling.

    Returns:
        float: Score from 0 to 100.

    """
    if contributions_count <= 0:
        return 0.0
    return min(MAX_SCORE, math.log2(1 + contributions_count) * 10)


def _score_leadership(
    *,
    chapter_leader_count: int,
    project_leader_count: int,
    committee_member_count: int,
    is_board_member: bool,
    is_gsoc_mentor: bool,
    is_owasp_staff: bool,
) -> float:
    """Score based on community leadership roles.

    Returns:
        float: Score from 0 to 100.

    """
    score = 0.0
    score += min(project_leader_count * POINTS_PROJECT_LEADER, MAX_PROJECT_LEADER_POINTS)
    score += min(chapter_leader_count * POINTS_CHAPTER_LEADER, MAX_CHAPTER_LEADER_POINTS)
    score += min(committee_member_count * POINTS_COMMITTEE_MEMBER, MAX_COMMITTEE_MEMBER_POINTS)

    if is_board_member:
        score += POINTS_BOARD_MEMBER
    if is_gsoc_mentor:
        score += POINTS_GSOC_MENTOR
    if is_owasp_staff:
        score += POINTS_OWASP_STAFF

    return min(score, MAX_SCORE)


def _score_recency(contribution_data: dict | None) -> float:
    """Score based on recent contribution activity.

    Contributions are weighted by recency:
    - Last 90 days: weight 3x
    - 91-180 days: weight 2x
    - 181-365 days: weight 1x

    Returns:
        float: Score from 0 to 100.

    """
    if not contribution_data:
        return 0.0

    now = datetime.now(tz=UTC).date()
    window_90 = now - timedelta(days=90)
    window_180 = now - timedelta(days=180)
    window_365 = now - timedelta(days=365)

    recent_90: float = 0.0
    recent_180: float = 0.0
    recent_365: float = 0.0

    for date_str, count in contribution_data.items():
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC).date()
            numeric_count = float(count)
        except (ValueError, TypeError):
            continue

        if numeric_count <= 0:
            continue

        if date >= window_90:
            recent_90 += numeric_count
        elif date >= window_180:
            recent_180 += numeric_count
        elif date >= window_365:
            recent_365 += numeric_count

    weighted_sum = recent_90 * 3 + recent_180 * 2 + recent_365 * 1

    if weighted_sum <= 0:
        return 0.0

    return min(MAX_SCORE, math.log2(1 + weighted_sum) * 8)


def _score_breadth(distinct_repository_count: int) -> float:
    """Score based on the number of distinct repositories contributed to.

    Returns:
        float: Score from 0 to 100.

    """
    return min(MAX_SCORE, distinct_repository_count * 10)


def _score_releases(release_count: int) -> float:
    """Score based on how many releases a user has authored.

    Uses logarithmic scaling with a higher multiplier since
    releases are high-impact but infrequent events.

    Returns:
        float: Score from 0 to 100.

    """
    if release_count <= 0:
        return 0.0
    return min(MAX_SCORE, math.log2(1 + release_count) * 20)


def _score_type_diversity(
    *,
    has_contributions: bool,
    has_pull_requests: bool,
    has_issues: bool,
    has_releases: bool,
) -> float:
    """Score based on diversity of contribution types.

    Awards 25 points each for having: commits, PRs, issues, releases.

    Returns:
        float: Score from 0 to 100.

    """
    score = 0.0
    if has_contributions:
        score += 25
    if has_pull_requests:
        score += 25
    if has_issues:
        score += 25
    if has_releases:
        score += 25
    return score


def _score_consistency(contribution_data: dict | None) -> float:
    """Score based on regularity of activity.

    Calculates the ratio of active days to total days in the
    contribution data period.

    Returns:
        float: Score from 0 to 100.

    """
    if not contribution_data:
        return 0.0

    total_days = len(contribution_data)
    if total_days == 0:
        return 0.0

    active_days = 0
    for count in contribution_data.values():
        try:
            if float(count) > 0:
                active_days += 1
        except (ValueError, TypeError):
            continue

    return min(MAX_SCORE, (active_days / total_days) * MAX_SCORE)
