"""Member ranking score calculation for OWASP Nest."""

from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta

WEIGHT_CONTRIBUTIONS = 0.35
WEIGHT_LEADERSHIP = 0.25
WEIGHT_RECENCY = 0.20
WEIGHT_BREADTH = 0.10
WEIGHT_CONSISTENCY = 0.10

POINTS_BOARD_MEMBER = 50
POINTS_PROJECT_LEADER = 20
POINTS_CHAPTER_LEADER = 15
POINTS_COMMITTEE_MEMBER = 10
POINTS_GSOC_MENTOR = 10

RECENCY_WINDOW_DAYS = 90
CONSISTENCY_WEEKS = 52


def calculate_member_score(
    *,
    contributions_count: int,
    distinct_repository_count: int,
    chapter_leader_count: int,
    project_leader_count: int,
    committee_member_count: int,
    is_board_member: bool,
    is_gsoc_mentor: bool,
    contribution_data: dict | None,
) -> float:
    """Calculate a member's ranking score (0-100) based on contributions and roles."""
    score = (
        WEIGHT_CONTRIBUTIONS * _contributions_score(contributions_count)
        + WEIGHT_LEADERSHIP
        * _leadership_score(
            chapter_leader_count=chapter_leader_count,
            project_leader_count=project_leader_count,
            committee_member_count=committee_member_count,
            is_board_member=is_board_member,
            is_gsoc_mentor=is_gsoc_mentor,
        )
        + WEIGHT_RECENCY * _recency_score(contribution_data)
        + WEIGHT_BREADTH * _breadth_score(distinct_repository_count)
        + WEIGHT_CONSISTENCY * _consistency_score(contribution_data)
    )

    return round(score, 2)


def _contributions_score(contributions_count: int) -> float:
    """Calculate contribution score using log scaling (0-100)."""
    if contributions_count <= 0:
        return 0.0
    return min(100.0, math.log2(1 + contributions_count) * 10.0)


def _leadership_score(
    *,
    chapter_leader_count: int,
    project_leader_count: int,
    committee_member_count: int,
    is_board_member: bool,
    is_gsoc_mentor: bool,
) -> float:
    """Calculate leadership score from community roles (0-80)."""
    score = (
        int(is_board_member) * POINTS_BOARD_MEMBER
        + project_leader_count * POINTS_PROJECT_LEADER
        + chapter_leader_count * POINTS_CHAPTER_LEADER
        + committee_member_count * POINTS_COMMITTEE_MEMBER
        + int(is_gsoc_mentor) * POINTS_GSOC_MENTOR
    )
    return min(80.0, score)


def _recency_score(contribution_data: dict | None) -> float:
    """Calculate recency score from contributions in the last 90 days (0-100)."""
    if not contribution_data:
        return 0.0

    now = datetime.now(tz=UTC)
    window_start = now - timedelta(days=RECENCY_WINDOW_DAYS)
    recent_contributions = 0.0

    for date_str, count in contribution_data.items():
        try:
            numeric_count = float(count)
            if numeric_count <= 0:
                continue
            date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC)
        except (ValueError, TypeError):
            continue

        if date >= window_start:
            recent_contributions += numeric_count

    return min(100.0, math.log1p(recent_contributions) * 15.0)


def _breadth_score(distinct_repository_count: int) -> float:
    """Calculate breadth score from distinct repositories contributed to (0-100)."""
    if distinct_repository_count <= 0:
        return 0.0
    return min(100.0, math.log2(1 + distinct_repository_count) * 15.0)


def _consistency_score(contribution_data: dict | None) -> float:
    """Calculate consistency score based on activity across the last 52 weeks (0-100)."""
    if not contribution_data:
        return 0.0

    now = datetime.now(tz=UTC)
    one_year_ago = now - timedelta(weeks=CONSISTENCY_WEEKS)
    active_weeks: set[tuple[int, int]] = set()

    for date_str, count in contribution_data.items():
        try:
            if float(count) <= 0:
                continue
            date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC)
        except (ValueError, TypeError):
            continue

        if date >= one_year_ago:
            active_weeks.add((date.isocalendar().year, date.isocalendar().week))

    return min(100.0, round(len(active_weeks) / CONSISTENCY_WEEKS * 100.0, 2))
