"""Tests for MemberScoreCalculator service."""

import math
from datetime import UTC, datetime, timedelta

import pytest

from apps.github.services.score import (
    MAX_SCORE,
    POINTS_BOARD_MEMBER,
    POINTS_CHAPTER_LEADER,
    POINTS_COMMITTEE_MEMBER,
    POINTS_GSOC_MENTOR,
    POINTS_OWASP_STAFF,
    POINTS_PROJECT_LEADER,
    WEIGHT_BREADTH,
    WEIGHT_CONSISTENCY,
    WEIGHT_CONTRIBUTIONS,
    WEIGHT_LEADERSHIP,
    WEIGHT_RECENCY,
    WEIGHT_RELEASES,
    WEIGHT_TYPE_DIVERSITY,
    _score_breadth,
    _score_consistency,
    _score_contributions,
    _score_leadership,
    _score_recency,
    _score_releases,
    _score_type_diversity,
    calculate_member_score,
)


class TestScoreContributions:
    """Tests for contribution score calculation."""

    def test_zero_contributions(self):
        """Test that zero contributions gives zero score."""
        assert _score_contributions(0) == pytest.approx(0.0)

    def test_negative_contributions(self):
        """Test that negative contributions gives zero score."""
        assert _score_contributions(-1) == pytest.approx(0.0)

    def test_positive_contributions(self):
        """Test that positive contributions give a positive score."""
        score = _score_contributions(100)
        assert score > 0.0

    def test_logarithmic_scaling(self):
        """Test that score uses logarithmic scaling."""
        expected = min(MAX_SCORE, math.log2(101) * 10)
        assert math.isclose(_score_contributions(100), expected)

    def test_cap_at_100(self):
        """Test that very large contribution counts are capped at 100."""
        assert _score_contributions(100000) == MAX_SCORE


class TestScoreLeadership:
    """Tests for leadership score calculation."""

    def test_no_leadership_roles(self):
        """Test zero score when user has no leadership roles."""
        score = _score_leadership(
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
            is_owasp_staff=False,
        )
        assert score == pytest.approx(0.0)

    def test_project_leader(self):
        """Test score for a single project leader role."""
        score = _score_leadership(
            chapter_leader_count=0,
            project_leader_count=1,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
            is_owasp_staff=False,
        )
        assert score == POINTS_PROJECT_LEADER

    def test_chapter_leader(self):
        """Test score for chapter leader roles."""
        score = _score_leadership(
            chapter_leader_count=2,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
            is_owasp_staff=False,
        )
        assert score == 2 * POINTS_CHAPTER_LEADER

    def test_committee_member(self):
        """Test score for committee membership."""
        score = _score_leadership(
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=1,
            is_board_member=False,
            is_gsoc_mentor=False,
            is_owasp_staff=False,
        )
        assert score == POINTS_COMMITTEE_MEMBER

    def test_board_member_bonus(self):
        """Test board member bonus points."""
        score = _score_leadership(
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=True,
            is_gsoc_mentor=False,
            is_owasp_staff=False,
        )
        assert score == POINTS_BOARD_MEMBER

    def test_gsoc_mentor_bonus(self):
        """Test GSoC mentor bonus points."""
        score = _score_leadership(
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=True,
            is_owasp_staff=False,
        )
        assert score == POINTS_GSOC_MENTOR

    def test_owasp_staff_bonus(self):
        """Test OWASP staff bonus points."""
        score = _score_leadership(
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
            is_owasp_staff=True,
        )
        assert score == POINTS_OWASP_STAFF

    def test_capped_at_100(self):
        """Test that leadership score is capped at 100."""
        score = _score_leadership(
            chapter_leader_count=10,
            project_leader_count=10,
            committee_member_count=10,
            is_board_member=True,
            is_gsoc_mentor=True,
            is_owasp_staff=True,
        )
        assert score == MAX_SCORE

    def test_all_roles_combined(self):
        """Test combined score for all roles."""
        score = _score_leadership(
            chapter_leader_count=1,
            project_leader_count=1,
            committee_member_count=1,
            is_board_member=True,
            is_gsoc_mentor=True,
            is_owasp_staff=True,
        )
        expected = min(
            MAX_SCORE,
            POINTS_PROJECT_LEADER
            + POINTS_CHAPTER_LEADER
            + POINTS_COMMITTEE_MEMBER
            + POINTS_BOARD_MEMBER
            + POINTS_GSOC_MENTOR
            + POINTS_OWASP_STAFF,
        )
        assert score == expected


class TestScoreRecency:
    """Tests for recency score calculation."""

    def test_no_contribution_data(self):
        """Test zero score when no contribution data exists."""
        assert _score_recency({}) == pytest.approx(0.0)

    def test_none_contribution_data(self):
        """Test zero score when contribution_data is None."""
        assert _score_recency(None) == pytest.approx(0.0)

    def test_recent_contributions_weighted_higher(self):
        """Test that recent contributions produce higher scores."""
        now = datetime.now(tz=UTC).date()

        recent_data = {(now - timedelta(days=i)).strftime("%Y-%m-%d"): 1 for i in range(30)}
        old_data = {(now - timedelta(days=i)).strftime("%Y-%m-%d"): 1 for i in range(200, 230)}

        assert _score_recency(recent_data) > _score_recency(old_data)

    def test_invalid_date_ignored(self):
        """Test that invalid dates are skipped."""
        assert _score_recency({"not-a-date": 5}) == pytest.approx(0.0)

    def test_non_numeric_count_ignored(self):
        """Test that non-numeric counts are skipped."""
        assert _score_recency({"2025-01-01": "invalid"}) == pytest.approx(0.0)

    def test_zero_count_skipped(self):
        """Test that days with zero contributions are not counted."""
        now = datetime.now(tz=UTC).date()
        data = {(now - timedelta(days=5)).strftime("%Y-%m-%d"): 0}
        assert _score_recency(data) == pytest.approx(0.0)

    def test_180_day_window_scored(self):
        """Test that contributions in the 91-180 day window are scored."""
        now = datetime.now(tz=UTC).date()
        date_120 = (now - timedelta(days=120)).strftime("%Y-%m-%d")
        assert _score_recency({date_120: 10}) > 0.0

    def test_365_day_window_scored(self):
        """Test that contributions in the 181-365 day window are scored."""
        now = datetime.now(tz=UTC).date()
        date_250 = (now - timedelta(days=250)).strftime("%Y-%m-%d")
        assert _score_recency({date_250: 10}) > 0.0

    def test_180_day_window_less_than_90_day(self):
        """Test that 90-day contributions score higher than 180-day ones."""
        now = datetime.now(tz=UTC).date()
        recent = {(now - timedelta(days=5)).strftime("%Y-%m-%d"): 10}
        mid = {(now - timedelta(days=120)).strftime("%Y-%m-%d"): 10}
        assert _score_recency(recent) > _score_recency(mid)


class TestScoreBreadth:
    """Tests for breadth score calculation."""

    def test_no_repos(self):
        """Test zero score with no repository contributions."""
        assert _score_breadth(0) == 0

    def test_multiple_repos(self):
        """Test score scales with number of repos."""
        assert _score_breadth(5) == 50

    def test_capped_at_100(self):
        """Test breadth score is capped at 100."""
        assert _score_breadth(20) == MAX_SCORE


class TestScoreReleases:
    """Tests for release score calculation."""

    def test_zero_releases(self):
        """Test that zero releases gives zero score."""
        assert _score_releases(0) == pytest.approx(0.0)

    def test_negative_releases(self):
        """Test that negative values give zero score."""
        assert _score_releases(-3) == pytest.approx(0.0)

    def test_single_release(self):
        """Test score for a single release."""
        score = _score_releases(1)
        assert score == pytest.approx(math.log2(2) * 20)

    def test_several_releases(self):
        """Test that more releases give higher score."""
        assert _score_releases(10) > _score_releases(3)

    def test_capped_at_100(self):
        """Test that release score is capped at 100."""
        assert _score_releases(10000) == MAX_SCORE


class TestScoreTypeDiversity:
    """Tests for type diversity score calculation."""

    def test_no_contributions(self):
        """Test zero score with no contribution types."""
        score = _score_type_diversity(
            has_contributions=False,
            has_pull_requests=False,
            has_issues=False,
            has_releases=False,
        )
        assert score == 0

    def test_all_types(self):
        """Test full score with all contribution types."""
        score = _score_type_diversity(
            has_contributions=True,
            has_pull_requests=True,
            has_issues=True,
            has_releases=True,
        )
        assert score == MAX_SCORE

    def test_partial_types(self):
        """Test partial score with some contribution types."""
        score = _score_type_diversity(
            has_contributions=True,
            has_pull_requests=True,
            has_issues=False,
            has_releases=False,
        )
        assert score == 50


class TestScoreConsistency:
    """Tests for consistency score calculation."""

    def test_no_data(self):
        """Test zero score with no contribution data."""
        assert _score_consistency({}) == pytest.approx(0.0)

    def test_none_data(self):
        """Test zero score with None data."""
        assert _score_consistency(None) == pytest.approx(0.0)

    def test_all_active_days(self):
        """Test full score when all days are active."""
        data = {f"2025-01-{i:02d}": 1 for i in range(1, 31)}
        assert _score_consistency(data) == MAX_SCORE

    def test_partial_active_days(self):
        """Test partial score with some inactive days."""
        data = {}
        for i in range(1, 11):
            data[f"2025-01-{i:02d}"] = 1
        for i in range(11, 21):
            data[f"2025-01-{i:02d}"] = 0
        assert math.isclose(_score_consistency(data), 50)

    def test_zero_count_not_active(self):
        """Test that days with count=0 are not counted as active."""
        data = {f"2025-01-{i:02d}": 0 for i in range(1, 31)}
        assert _score_consistency(data) == pytest.approx(0.0)

    def test_non_numeric_count_skipped(self):
        """Test that non-numeric counts are skipped gracefully."""
        data = {"2025-01-01": "bad", "2025-01-02": 1}
        score = _score_consistency(data)
        # Only 1 of 2 days is valid and active
        assert math.isclose(score, 50)


class TestCalculateMemberScore:
    """Tests for end-to-end score calculation."""

    def _make_score(self, **overrides):
        """Create a score with sensible defaults, overridden by kwargs."""
        defaults = {
            "contributions_count": 0,
            "distinct_repository_count": 0,
            "release_count": 0,
            "chapter_leader_count": 0,
            "project_leader_count": 0,
            "committee_member_count": 0,
            "is_board_member": False,
            "is_gsoc_mentor": False,
            "is_owasp_staff": False,
            "has_pull_requests": False,
            "has_issues": False,
            "has_releases": False,
            "has_contributions": False,
            "contribution_data": None,
        }
        defaults.update(overrides)
        return calculate_member_score(**defaults)

    def test_all_zeros(self):
        """Test that a user with no data gets zero score."""
        assert self._make_score() == pytest.approx(0.0)

    def test_contributions_only(self):
        """Test that contributions alone produce a positive score."""
        score = self._make_score(contributions_count=100)
        assert score > 0.0

    def test_leadership_boosts_score(self):
        """Test that leadership roles increase the score."""
        base = self._make_score(contributions_count=100)
        with_leadership = self._make_score(
            contributions_count=100,
            project_leader_count=1,
            chapter_leader_count=1,
            is_board_member=True,
        )
        assert with_leadership > base

    def test_recency_boosts_score(self):
        """Test that recent contributions increase the score."""
        now = datetime.now(tz=UTC)
        recent_data = {now.strftime("%Y-%m-%d"): 10}

        base = self._make_score(contributions_count=100)
        with_recency = self._make_score(
            contributions_count=100,
            contribution_data=recent_data,
        )
        assert with_recency > base

    def test_score_is_rounded(self):
        """Test that the final score is rounded to 2 decimal places."""
        score = self._make_score(contributions_count=123, distinct_repository_count=7)
        assert score == round(score, 2)

    def test_weights_sum_to_one(self):
        """Test that all weights sum to 1.0."""
        total = (
            WEIGHT_CONTRIBUTIONS
            + WEIGHT_LEADERSHIP
            + WEIGHT_RECENCY
            + WEIGHT_BREADTH
            + WEIGHT_TYPE_DIVERSITY
            + WEIGHT_RELEASES
            + WEIGHT_CONSISTENCY
        )
        assert total == pytest.approx(1.0)

    def test_weighted_calculation(self):
        """Test that the score is correctly weighted."""
        score = self._make_score(
            contributions_count=100,
            project_leader_count=1,
            distinct_repository_count=5,
            has_contributions=True,
            has_pull_requests=True,
        )
        assert score > 0.0
        assert score == round(score, 2)
