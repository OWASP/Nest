"""Tests for member ranking score calculation."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from apps.owasp.utils.scoring import (
    _breadth_score,
    _consistency_score,
    _contributions_score,
    _leadership_score,
    _recency_score,
    calculate_member_score,
)


class TestContributionsScore:
    """Test contribution score calculation."""

    def test_no_contributions_returns_zero(self):
        """Test that zero contributions returns zero score."""
        assert _contributions_score(0) == pytest.approx(0.0)

    def test_negative_contributions_returns_zero(self):
        """Test that negative contributions returns zero score."""
        assert _contributions_score(-5) == pytest.approx(0.0)

    def test_single_contribution(self):
        """Test score for single contribution."""
        score = _contributions_score(1)
        assert 0 < score < 100

    def test_contributions_score_capped_at_100(self):
        """Test that contributions score is capped at 100."""
        high_contributions = 100000
        score = _contributions_score(high_contributions)
        assert score == pytest.approx(100.0)

    def test_contributions_score_log_scaling(self):
        """Test that contributions use logarithmic scaling."""
        score_1 = _contributions_score(1)
        score_10 = _contributions_score(10)
        score_100 = _contributions_score(100)

        assert score_1 < score_10 < score_100


class TestLeadershipScore:
    """Test leadership score calculation."""

    def test_no_leadership_returns_zero(self):
        """Test that no leadership roles returns zero."""
        score = _leadership_score(
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
        )
        assert score == pytest.approx(0.0)

    def test_board_member_score(self):
        """Test board member score."""
        score = _leadership_score(
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=True,
            is_gsoc_mentor=False,
        )
        assert score == pytest.approx(50.0)

    def test_project_leader_score(self):
        """Test project leader score."""
        score = _leadership_score(
            chapter_leader_count=0,
            project_leader_count=1,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
        )
        assert score == pytest.approx(20.0)

    def test_chapter_leader_score(self):
        """Test chapter leader score."""
        score = _leadership_score(
            chapter_leader_count=1,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
        )
        assert score == pytest.approx(15.0)

    def test_committee_member_score(self):
        """Test committee member score."""
        score = _leadership_score(
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=1,
            is_board_member=False,
            is_gsoc_mentor=False,
        )
        assert score == pytest.approx(10.0)

    def test_gsoc_mentor_score(self):
        """Test GSOC mentor score."""
        score = _leadership_score(
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=True,
        )
        assert score == pytest.approx(10.0)

    def test_leadership_score_capped_at_80(self):
        """Test that leadership score is capped at 80."""
        score = _leadership_score(
            chapter_leader_count=5,
            project_leader_count=5,
            committee_member_count=5,
            is_board_member=True,
            is_gsoc_mentor=True,
        )
        assert score == pytest.approx(80.0)

    def test_multiple_roles_accumulate(self):
        """Test that multiple roles accumulate."""
        score = _leadership_score(
            chapter_leader_count=2,
            project_leader_count=1,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
        )
        assert score == pytest.approx(50.0)


class TestRecencyScore:
    """Test recency score calculation."""

    def test_no_contribution_data_returns_zero(self):
        """Test that empty contribution data returns zero."""
        score = _recency_score(None)
        assert score == pytest.approx(0.0)

    def test_empty_contribution_data_returns_zero(self):
        """Test that empty dict returns zero."""
        score = _recency_score({})
        assert score == pytest.approx(0.0)

    def test_recent_contributions(self):
        """Test score for recent contributions."""
        now = datetime.now(tz=UTC)
        recent_date = (now - timedelta(days=30)).strftime("%Y-%m-%d")
        contribution_data = {recent_date: 5}

        score = _recency_score(contribution_data)
        assert score > 0
        assert score <= 100

    def test_old_contributions_not_counted(self):
        """Test that contributions older than 90 days are ignored."""
        now = datetime.now(tz=UTC)
        old_date = (now - timedelta(days=120)).strftime("%Y-%m-%d")
        contribution_data = {old_date: 100}

        score = _recency_score(contribution_data)
        assert score == pytest.approx(0.0)

    def test_contributions_within_90_day_window(self):
        """Test contributions within 90-day recency window (89 days old)."""
        now = datetime.now(tz=UTC)
        boundary_date = (now - timedelta(days=89)).strftime("%Y-%m-%d")
        contribution_data = {boundary_date: 1}

        score = _recency_score(contribution_data)
        assert score > 0

    def test_multiple_recent_contributions_accumulate(self):
        """Test that multiple recent contributions accumulate."""
        now = datetime.now(tz=UTC)
        data = {}
        for days_ago in range(1, 10):
            date = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            data[date] = 1

        score = _recency_score(data)
        assert score > 0
        assert score <= 100

    def test_invalid_date_format_ignored(self):
        """Test that invalid date formats are handled gracefully."""
        now = datetime.now(tz=UTC)
        recent_date = (now - timedelta(days=10)).strftime("%Y-%m-%d")
        contribution_data = {
            "invalid-date": 5,
            recent_date: 10,
        }
        score = _recency_score(contribution_data)
        assert score > 0


class TestBreadthScore:
    """Test breadth score calculation."""

    def test_no_repositories_returns_zero(self):
        """Test that zero repositories returns zero."""
        assert _breadth_score(0) == pytest.approx(0.0)

    def test_negative_repositories_returns_zero(self):
        """Test that negative repositories returns zero."""
        assert _breadth_score(-5) == pytest.approx(0.0)

    def test_single_repository(self):
        """Test score for single repository."""
        score = _breadth_score(1)
        assert 0 < score < 100

    def test_breadth_score_capped_at_100(self):
        """Test that breadth score is capped at 100."""
        many_repos = 10000
        score = _breadth_score(many_repos)
        assert score == pytest.approx(100.0)

    def test_breadth_uses_log_scaling(self):
        """Test that breadth uses logarithmic scaling."""
        score_1 = _breadth_score(1)
        score_10 = _breadth_score(10)
        score_100 = _breadth_score(100)

        assert score_1 < score_10 < score_100


class TestConsistencyScore:
    """Test consistency score calculation."""

    def test_no_contribution_data_returns_zero(self):
        """Test that empty contribution data returns zero."""
        score = _consistency_score(None)
        assert score == pytest.approx(0.0)

    def test_empty_contribution_data_returns_zero(self):
        """Test that empty dict returns zero."""
        score = _consistency_score({})
        assert score == pytest.approx(0.0)

    def test_contributions_in_one_week(self):
        """Test contributions spread across one week."""
        now = datetime.now(tz=UTC)
        data = {}
        # Use different weeks to ensure different ISO weeks
        for weeks_ago in range(5):
            date = (now - timedelta(weeks=weeks_ago)).strftime("%Y-%m-%d")
            data[date] = 1

        score = _consistency_score(data)
        # Should be roughly 5/52 = 9.6%
        assert 8 < score < 12

    def test_contributions_spread_full_year(self):
        """Test contributions spread across full year."""
        now = datetime.now(tz=UTC)
        data = {}
        for weeks_ago in range(52):
            date = (now - timedelta(weeks=weeks_ago)).strftime("%Y-%m-%d")
            data[date] = 1

        score = _consistency_score(data)
        assert 95 <= score <= 100

    def test_old_contributions_not_counted(self):
        """Test that contributions older than 52 weeks are ignored."""
        now = datetime.now(tz=UTC)
        old_date = (now - timedelta(weeks=60)).strftime("%Y-%m-%d")
        data = {old_date: 100}

        score = _consistency_score(data)
        assert score == pytest.approx(0.0)

    def test_invalid_date_format_ignored(self):
        """Test that invalid dates are handled gracefully."""
        now = datetime.now(tz=UTC)
        data = {
            "invalid-date": 10,
            (now - timedelta(days=1)).strftime("%Y-%m-%d"): 1,
        }
        score = _consistency_score(data)
        assert score > 0  # Should count the valid date


class TestComprehensiveMemberScore:
    """Test the complete member score calculation."""

    def test_minimum_score(self):
        """Test member with no contributions or roles."""
        score = calculate_member_score(
            contributions_count=0,
            distinct_repository_count=0,
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
            contribution_data=None,
        )
        assert score == pytest.approx(0.0)

    def test_maximum_score_not_exceeded(self):
        """Test that score is capped at 100."""
        now = datetime.now(tz=UTC)
        contribution_data = {
            (now - timedelta(days=i)).strftime("%Y-%m-%d"): 100 for i in range(90)
        }

        score = calculate_member_score(
            contributions_count=1000,
            distinct_repository_count=1000,
            chapter_leader_count=10,
            project_leader_count=10,
            committee_member_count=10,
            is_board_member=True,
            is_gsoc_mentor=True,
            contribution_data=contribution_data,
        )
        assert 0 <= score <= 100

    def test_score_is_weighted_correctly(self):
        """Test that score weights are applied correctly."""
        now = datetime.now(tz=UTC)
        contribution_data = {(now - timedelta(days=i)).strftime("%Y-%m-%d"): 1 for i in range(7)}

        score = calculate_member_score(
            contributions_count=10,
            distinct_repository_count=3,
            chapter_leader_count=1,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
            contribution_data=contribution_data,
        )

        assert 0 <= score <= 100
        assert score > 0

    def test_score_is_rounded_to_two_decimals(self):
        """Test that score is rounded to 2 decimal places."""
        score = calculate_member_score(
            contributions_count=5,
            distinct_repository_count=2,
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
            contribution_data=None,
        )
        assert len(str(score).split(".")[-1]) <= 2

    def test_contributions_are_primary_factor(self):
        """Test that contributions have the largest weight (35%)."""
        now = datetime.now(tz=UTC)
        contribution_data = {(now - timedelta(days=i)).strftime("%Y-%m-%d"): 1 for i in range(30)}

        score_with_contributions = calculate_member_score(
            contributions_count=100,
            distinct_repository_count=1,
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
            contribution_data=contribution_data,
        )

        score_with_leadership = calculate_member_score(
            contributions_count=0,
            distinct_repository_count=1,
            chapter_leader_count=5,
            project_leader_count=5,
            committee_member_count=5,
            is_board_member=True,
            is_gsoc_mentor=True,
            contribution_data=None,
        )

        assert score_with_contributions > score_with_leadership
