"""Member scoring algorithm for OWASP Nest ranking."""

from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta

WEIGHT_CONTRIBUTIONS = 0.25
WEIGHT_LEADERSHIP = 0.20
WEIGHT_BREADTH = 0.10
WEIGHT_RELEASES = 0.10
WEIGHT_RECENCY = 0.20
WEIGHT_CONSISTENCY = 0.15

BONUS_CHAPTER_LEADER = 10.0
BONUS_PROJECT_LEADER = 10.0
BONUS_COMMITTEE_MEMBER = 8.0
BONUS_BOARD_MEMBER = 15.0
BONUS_GSOC_MENTOR = 5.0

RECENCY_HALF_LIFE_DAYS = 365

RELEASE_WEIGHT_MULTIPLIER = 3.0


def calculate_member_score(
    *,
    contributions_count: int,
    distinct_repository_count: int,
    distinct_project_count: int,
    release_count: int,
    chapter_leader_count: int,
    project_leader_count: int,
    committee_member_count: int,
    is_board_member: bool,
    is_gsoc_mentor: bool,
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
    )
    breadth_score = _score_breadth(distinct_repository_count, distinct_project_count)
    releases_score = _score_releases(release_count)
    recency_score = _score_recency(contribution_data)
    consistency_score = _score_consistency(contribution_data)

    total = (
        WEIGHT_CONTRIBUTIONS * contributions_score
        + WEIGHT_LEADERSHIP * leadership_score
        + WEIGHT_BREADTH * breadth_score
        + WEIGHT_RELEASES * releases_score
        + WEIGHT_RECENCY * recency_score
        + WEIGHT_CONSISTENCY * consistency_score
    )

    return round(total, 4)


def _score_contributions(contributions_count: int) -> float:
    """Score based on total contributions using logarithmic scaling."""
    return math.log1p(max(contributions_count, 0)) * 10.0


def _score_leadership(
    *,
    chapter_leader_count: int,
    project_leader_count: int,
    committee_member_count: int,
    is_board_member: bool,
    is_gsoc_mentor: bool,
) -> float:
    """Score based on community leadership roles."""
    return (
        chapter_leader_count * BONUS_CHAPTER_LEADER
        + project_leader_count * BONUS_PROJECT_LEADER
        + committee_member_count * BONUS_COMMITTEE_MEMBER
        + int(is_board_member) * BONUS_BOARD_MEMBER
        + int(is_gsoc_mentor) * BONUS_GSOC_MENTOR
    )


def _score_breadth(distinct_repository_count: int, distinct_project_count: int) -> float:
    """Score based on breadth of contributions across repositories or projects.

    Uses log scaling to reward breadth while diminishing returns for
    extremely large numbers.
    """
    repo_score = math.log1p(distinct_repository_count) * 8.0
    project_score = math.log1p(distinct_project_count) * 12.0
    return repo_score + project_score


def _score_releases(release_count: int) -> float:
    """Score based on release creation, weighted higher than regular contributions."""
    return math.log1p(max(release_count, 0)) * RELEASE_WEIGHT_MULTIPLIER * 10.0


def _score_recency(contribution_data: dict | None) -> float:
    """Score based on recency of contributions.

    More recent contributions are worth more via exponential decay.
    """
    if not contribution_data:
        return 0.0

    now = datetime.now(tz=UTC)
    total_score = 0.0

    for date_str, count in contribution_data.items():
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC)
            days_ago = max((now - date).days, 0)
        except (ValueError, TypeError):
            continue

        decay = 0.5 ** (days_ago / RECENCY_HALF_LIFE_DAYS)
        total_score += count * decay

    return math.log1p(total_score) * 10.0


def _score_consistency(contribution_data: dict | None) -> float:
    """Score based on contribution consistency over time.

    Measures what fraction of weeks in the past year had at least one contribution.
    """
    if not contribution_data:
        return 0.0

    now = datetime.now(tz=UTC)
    one_year_ago = now - timedelta(days=365)

    active_weeks: set[tuple[int, int]] = set()

    for date_str, count in contribution_data.items():
        if count <= 0:
            continue
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC)
        except (ValueError, TypeError):
            continue

        if date >= one_year_ago:
            year, week, _ = date.isocalendar()
            active_weeks.add((year, week))

    consistency_ratio = min(len(active_weeks) / 52, 1.0)
    return consistency_ratio * 50.0
