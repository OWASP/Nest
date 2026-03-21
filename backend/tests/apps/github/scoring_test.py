"""Tests for the member scoring algorithm."""

from datetime import UTC, datetime, timedelta

import pytest

from apps.github.scoring import (
    BONUS_BOARD_MEMBER,
    BONUS_CHAPTER_LEADER,
    BONUS_COMMITTEE_MEMBER,
    BONUS_GSOC_MENTOR,
    BONUS_PROJECT_LEADER,
    WEIGHT_BREADTH,
    WEIGHT_CONSISTENCY,
    WEIGHT_CONTRIBUTIONS,
    WEIGHT_LEADERSHIP,
    WEIGHT_RECENCY,
    WEIGHT_RELEASES,
    _score_breadth,
    _score_consistency,
    _score_contributions,
    _score_leadership,
    _score_recency,
    _score_releases,
    calculate_member_score,
)


class TestScoreContributions:
    def test_zero_contributions(self):
        assert _score_contributions(0) == pytest.approx(0.0)

    def test_negative_contributions(self):
        assert _score_contributions(-1) == pytest.approx(0.0)

    def test_positive_contributions(self):
        score = _score_contributions(100)
        assert score > 0.0

    def test_logarithmic_scaling(self):
        """Higher contributions give diminishing returns."""
        score_100 = _score_contributions(100)
        score_1000 = _score_contributions(1000)
        score_10000 = _score_contributions(10000)
        assert score_1000 > score_100
        assert score_10000 > score_1000

        ratio_1 = score_1000 / score_100
        ratio_2 = score_10000 / score_1000
        assert abs(ratio_1 - ratio_2) < ratio_1 * 0.5


class TestScoreLeadership:
    def test_no_leadership(self):
        score = _score_leadership(
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
        )
        assert score == pytest.approx(0.0)

    def test_chapter_leader(self):
        score = _score_leadership(
            chapter_leader_count=2,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
        )
        assert score == 2 * BONUS_CHAPTER_LEADER

    def test_project_leader(self):
        score = _score_leadership(
            chapter_leader_count=0,
            project_leader_count=3,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
        )
        assert score == 3 * BONUS_PROJECT_LEADER

    def test_committee_member(self):
        score = _score_leadership(
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=1,
            is_board_member=False,
            is_gsoc_mentor=False,
        )
        assert score == BONUS_COMMITTEE_MEMBER

    def test_board_member(self):
        score = _score_leadership(
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=True,
            is_gsoc_mentor=False,
        )
        assert score == BONUS_BOARD_MEMBER

    def test_gsoc_mentor(self):
        score = _score_leadership(
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=True,
        )
        assert score == BONUS_GSOC_MENTOR

    def test_all_roles_combined(self):
        score = _score_leadership(
            chapter_leader_count=1,
            project_leader_count=1,
            committee_member_count=1,
            is_board_member=True,
            is_gsoc_mentor=True,
        )
        expected = (
            BONUS_CHAPTER_LEADER
            + BONUS_PROJECT_LEADER
            + BONUS_COMMITTEE_MEMBER
            + BONUS_BOARD_MEMBER
            + BONUS_GSOC_MENTOR
        )
        assert score == expected


class TestScoreBreadth:
    def test_zero_breadth(self):
        assert _score_breadth(0, 0) == pytest.approx(0.0)

    def test_repo_breadth(self):
        score = _score_breadth(5, 0)
        assert score > 0.0

    def test_project_breadth(self):
        score = _score_breadth(0, 3)
        assert score > 0.0

    def test_combined_breadth(self):
        score = _score_breadth(5, 3)
        repo_only = _score_breadth(5, 0)
        project_only = _score_breadth(0, 3)
        assert score == repo_only + project_only


class TestScoreReleases:
    def test_zero_releases(self):
        assert _score_releases(0) == pytest.approx(0.0)

    def test_negative_releases(self):
        assert _score_releases(-1) == pytest.approx(0.0)

    def test_positive_releases(self):
        score = _score_releases(5)
        assert score > 0.0

    def test_releases_higher_weight(self):
        """Releases should score higher per unit than regular contributions."""
        release_score = _score_releases(10)
        contrib_score = _score_contributions(10)
        assert release_score > contrib_score


class TestScoreRecency:
    def test_no_data(self):
        assert _score_recency(None) == pytest.approx(0.0)

    def test_empty_data(self):
        assert _score_recency({}) == pytest.approx(0.0)

    def test_recent_contributions_score_higher(self):
        """Contributions made today should score higher than those a year ago."""
        now = datetime.now(tz=UTC)
        recent_data = {now.strftime("%Y-%m-%d"): 10}
        old_data = {(now - timedelta(days=730)).strftime("%Y-%m-%d"): 10}
        assert _score_recency(recent_data) > _score_recency(old_data)

    def test_invalid_date_ignored(self):
        score = _score_recency({"not-a-date": 5})
        assert score == pytest.approx(0.0)

    def test_mixed_valid_invalid(self):
        now = datetime.now(tz=UTC)
        data = {
            now.strftime("%Y-%m-%d"): 5,
            "invalid": 10,
        }
        valid_only = {now.strftime("%Y-%m-%d"): 5}
        assert _score_recency(data) == _score_recency(valid_only)

    def test_nan_count_ignored(self):
        now = datetime.now(tz=UTC)
        score = _score_recency({now.strftime("%Y-%m-%d"): float("nan")})
        assert score == pytest.approx(0.0)

    def test_infinity_count_ignored(self):
        now = datetime.now(tz=UTC)
        score = _score_recency({now.strftime("%Y-%m-%d"): float("inf")})
        assert score == pytest.approx(0.0)


class TestScoreConsistency:
    def test_no_data(self):
        assert _score_consistency(None) == pytest.approx(0.0)

    def test_empty_data(self):
        assert _score_consistency({}) == pytest.approx(0.0)

    def test_single_week_activity(self):
        now = datetime.now(tz=UTC)
        data = {now.strftime("%Y-%m-%d"): 50}
        score = _score_consistency(data)
        assert 0 < score <= 50.0

    def test_full_year_consistency(self):
        """Activity every week for a year should give maximum score."""
        now = datetime.now(tz=UTC)
        data = {}
        for week in range(52):
            date = now - timedelta(weeks=week)
            data[date.strftime("%Y-%m-%d")] = 1
        score = _score_consistency(data)
        assert score == pytest.approx(50.0, abs=2.0)

    def test_old_data_excluded(self):
        """Contributions older than a year should not count for consistency."""
        now = datetime.now(tz=UTC)
        old_date = now - timedelta(days=400)
        data = {old_date.strftime("%Y-%m-%d"): 100}
        assert _score_consistency(data) == pytest.approx(0.0)


class TestCalculateMemberScore:
    def test_all_zeros(self):
        score = calculate_member_score(
            contributions_count=0,
            distinct_repository_count=0,
            distinct_project_count=0,
            release_count=0,
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
            contribution_data=None,
        )
        assert score == pytest.approx(0.0)

    def test_contributions_only(self):
        score = calculate_member_score(
            contributions_count=100,
            distinct_repository_count=0,
            distinct_project_count=0,
            release_count=0,
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
            contribution_data=None,
        )
        assert score > 0.0

    def test_leadership_boosts_score(self):
        base = calculate_member_score(
            contributions_count=100,
            distinct_repository_count=5,
            distinct_project_count=2,
            release_count=0,
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
            contribution_data=None,
        )
        with_leadership = calculate_member_score(
            contributions_count=100,
            distinct_repository_count=5,
            distinct_project_count=2,
            release_count=0,
            chapter_leader_count=2,
            project_leader_count=1,
            committee_member_count=1,
            is_board_member=True,
            is_gsoc_mentor=False,
            contribution_data=None,
        )
        assert with_leadership > base

    def test_recency_boosts_score(self):
        now = datetime.now(tz=UTC)
        recent_data = {now.strftime("%Y-%m-%d"): 10}
        base = calculate_member_score(
            contributions_count=100,
            distinct_repository_count=5,
            distinct_project_count=2,
            release_count=0,
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
            contribution_data=None,
        )
        with_recency = calculate_member_score(
            contributions_count=100,
            distinct_repository_count=5,
            distinct_project_count=2,
            release_count=0,
            chapter_leader_count=0,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
            contribution_data=recent_data,
        )
        assert with_recency > base

    def test_score_is_rounded(self):
        score = calculate_member_score(
            contributions_count=123,
            distinct_repository_count=7,
            distinct_project_count=3,
            release_count=2,
            chapter_leader_count=1,
            project_leader_count=0,
            committee_member_count=0,
            is_board_member=False,
            is_gsoc_mentor=False,
            contribution_data=None,
        )
        assert score == round(score, 4)

    def test_weights_sum_to_one(self):
        total = (
            WEIGHT_CONTRIBUTIONS
            + WEIGHT_LEADERSHIP
            + WEIGHT_BREADTH
            + WEIGHT_RELEASES
            + WEIGHT_RECENCY
            + WEIGHT_CONSISTENCY
        )
        assert total == pytest.approx(1.0)
