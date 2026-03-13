"""Tests for MemberScoreCalculator service."""

import math
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from apps.github.services.score import (
    MAX_SCORE,
    POINTS_BOARD_MEMBER,
    POINTS_OWASP_STAFF,
    WEIGHT_BREADTH,
    WEIGHT_CONSISTENCY,
    WEIGHT_CONTRIBUTIONS,
    WEIGHT_LEADERSHIP,
    WEIGHT_RECENCY,
    WEIGHT_TYPE_DIVERSITY,
    MemberScoreCalculator,
)


@pytest.fixture
def calculator():
    """Return a MemberScoreCalculator instance."""
    return MemberScoreCalculator()


@pytest.fixture
def mock_user():
    """Return a mock User instance with defaults."""
    user = MagicMock()
    user.contributions_count = 0
    user.calculated_score = 0
    user.is_owasp_staff = False
    user.contribution_data = {}
    user.created_pull_requests = MagicMock()
    user.created_pull_requests.exists.return_value = False
    user.created_issues = MagicMock()
    user.created_issues.exists.return_value = False
    user.created_releases = MagicMock()
    user.created_releases.exists.return_value = False

    type(user).owasp_profile = PropertyMock(side_effect=Exception("No profile"))

    return user


class TestContributionScore:
    """Tests for contribution score calculation."""

    def test_zero_contributions(self, calculator, mock_user):
        """Test that zero contributions gives zero score."""
        mock_user.contributions_count = 0
        assert calculator._contribution_score(mock_user) == 0

    def test_logarithmic_scaling(self, calculator, mock_user):
        """Test that score uses logarithmic scaling."""
        mock_user.contributions_count = 100
        expected = min(MAX_SCORE, math.log2(101) * 10)
        assert math.isclose(calculator._contribution_score(mock_user), expected)

    def test_cap_at_100(self, calculator, mock_user):
        """Test that very large contribution counts are capped at 100."""
        mock_user.contributions_count = 100000
        assert calculator._contribution_score(mock_user) == MAX_SCORE


class TestLeadershipScore:
    """Tests for leadership score calculation."""

    @patch("apps.owasp.models.entity_member.EntityMember.objects.filter")
    @patch("django.contrib.contenttypes.models.ContentType.objects.get_for_model")
    def test_no_leadership_roles(self, mock_ct, mock_em_filter, calculator, mock_user):
        """Test zero score when user has no leadership roles."""
        mock_qs = MagicMock()
        mock_qs.filter.return_value.count.return_value = 0
        mock_em_filter.return_value = mock_qs

        assert calculator._leadership_score(mock_user) == 0

    @patch("apps.owasp.models.entity_member.EntityMember.objects.filter")
    @patch("django.contrib.contenttypes.models.ContentType.objects.get_for_model")
    def test_project_leader(self, mock_ct, mock_em_filter, calculator, mock_user):
        """Test score for a single project leader role."""
        mock_qs = MagicMock()

        def filter_side_effect(**kwargs):
            mock_count = MagicMock()
            if (
                kwargs.get("role") == "leader"
                and kwargs.get("entity_type") == mock_ct.return_value
            ):
                mock_count.count.return_value = 1
            else:
                mock_count.count.return_value = 0
            return mock_count

        mock_qs.filter.side_effect = filter_side_effect
        mock_em_filter.return_value = mock_qs

        score = calculator._leadership_score(mock_user)
        assert score >= 0

    @patch("apps.owasp.models.entity_member.EntityMember.objects.filter")
    @patch("django.contrib.contenttypes.models.ContentType.objects.get_for_model")
    def test_board_member_bonus(self, mock_ct, mock_em_filter, calculator, mock_user):
        """Test board member bonus points."""
        mock_qs = MagicMock()
        mock_qs.filter.return_value.count.return_value = 0
        mock_em_filter.return_value = mock_qs

        profile = MagicMock()
        profile.is_owasp_board_member = True
        profile.is_gsoc_mentor = False
        type(mock_user).owasp_profile = PropertyMock(return_value=profile)

        score = calculator._leadership_score(mock_user)
        assert score == POINTS_BOARD_MEMBER

    @patch("apps.owasp.models.entity_member.EntityMember.objects.filter")
    @patch("django.contrib.contenttypes.models.ContentType.objects.get_for_model")
    def test_owasp_staff_bonus(self, mock_ct, mock_em_filter, calculator, mock_user):
        """Test OWASP staff bonus points."""
        mock_qs = MagicMock()
        mock_qs.filter.return_value.count.return_value = 0
        mock_em_filter.return_value = mock_qs
        mock_user.is_owasp_staff = True

        score = calculator._leadership_score(mock_user)
        assert score == POINTS_OWASP_STAFF

    @patch("apps.owasp.models.entity_member.EntityMember.objects.filter")
    @patch("django.contrib.contenttypes.models.ContentType.objects.get_for_model")
    def test_capped_at_100(self, mock_ct, mock_em_filter, calculator, mock_user):
        """Test that leadership score is capped at 100."""
        mock_qs = MagicMock()
        mock_qs.filter.return_value.count.return_value = 100
        mock_em_filter.return_value = mock_qs
        mock_user.is_owasp_staff = True

        profile = MagicMock()
        profile.is_owasp_board_member = True
        profile.is_gsoc_mentor = True
        type(mock_user).owasp_profile = PropertyMock(return_value=profile)

        score = calculator._leadership_score(mock_user)
        assert score == MAX_SCORE


class TestRecencyScore:
    """Tests for recency score calculation."""

    def test_no_contribution_data(self, calculator, mock_user):
        """Test zero score when no contribution data exists."""
        mock_user.contribution_data = {}
        assert calculator._recency_score(mock_user) == 0

    def test_none_contribution_data(self, calculator, mock_user):
        """Test zero score when contribution_data is None."""
        mock_user.contribution_data = None
        assert calculator._recency_score(mock_user) == 0

    def test_recent_contributions_weighted_higher(self, calculator, mock_user):
        """Test that recent contributions produce higher scores."""
        now = datetime.now(tz=UTC).date()

        recent_data = {(now - timedelta(days=i)).strftime("%Y-%m-%d"): 1 for i in range(30)}
        mock_user.contribution_data = recent_data
        recent_score = calculator._recency_score(mock_user)

        old_data = {(now - timedelta(days=i)).strftime("%Y-%m-%d"): 1 for i in range(200, 230)}
        mock_user.contribution_data = old_data
        old_score = calculator._recency_score(mock_user)

        assert recent_score > old_score


class TestBreadthScore:
    """Tests for breadth score calculation."""

    @patch("apps.github.models.repository_contributor.RepositoryContributor.objects.filter")
    def test_no_repos(self, mock_filter, calculator, mock_user):
        """Test zero score with no repository contributions."""
        mock_qs = MagicMock()
        mock_qs.exclude.return_value = mock_qs
        mock_qs.values.return_value = mock_qs
        mock_qs.distinct.return_value = mock_qs
        mock_qs.count.return_value = 0
        mock_filter.return_value = mock_qs

        assert calculator._breadth_score(mock_user) == 0

    @patch("apps.github.models.repository_contributor.RepositoryContributor.objects.filter")
    def test_multiple_repos(self, mock_filter, calculator, mock_user):
        """Test score scales with number of repos."""
        mock_qs = MagicMock()
        mock_qs.exclude.return_value = mock_qs
        mock_qs.values.return_value = mock_qs
        mock_qs.distinct.return_value = mock_qs
        mock_qs.count.return_value = 5
        mock_filter.return_value = mock_qs

        assert calculator._breadth_score(mock_user) == 50

    @patch("apps.github.models.repository_contributor.RepositoryContributor.objects.filter")
    def test_capped_at_100(self, mock_filter, calculator, mock_user):
        """Test breadth score is capped at 100."""
        mock_qs = MagicMock()
        mock_qs.exclude.return_value = mock_qs
        mock_qs.values.return_value = mock_qs
        mock_qs.distinct.return_value = mock_qs
        mock_qs.count.return_value = 20
        mock_filter.return_value = mock_qs

        assert calculator._breadth_score(mock_user) == MAX_SCORE


class TestTypeDiversityScore:
    """Tests for type diversity score calculation."""

    @patch("apps.github.models.repository_contributor.RepositoryContributor.objects.filter")
    def test_no_contributions(self, mock_filter, calculator, mock_user):
        """Test zero score with no contribution types."""
        mock_qs = MagicMock()
        mock_qs.exclude.return_value = mock_qs
        mock_qs.exists.return_value = False
        mock_filter.return_value = mock_qs

        assert calculator._type_diversity_score(mock_user) == 0

    @patch("apps.github.models.repository_contributor.RepositoryContributor.objects.filter")
    def test_all_types(self, mock_filter, calculator, mock_user):
        """Test full score with all contribution types."""
        mock_qs = MagicMock()
        mock_qs.exclude.return_value = mock_qs
        mock_qs.exists.return_value = True
        mock_filter.return_value = mock_qs

        mock_user.created_pull_requests.exists.return_value = True
        mock_user.created_issues.exists.return_value = True
        mock_user.created_releases.exists.return_value = True

        assert calculator._type_diversity_score(mock_user) == MAX_SCORE

    @patch("apps.github.models.repository_contributor.RepositoryContributor.objects.filter")
    def test_partial_types(self, mock_filter, calculator, mock_user):
        """Test partial score with some contribution types."""
        mock_qs = MagicMock()
        mock_qs.exclude.return_value = mock_qs
        mock_qs.exists.return_value = True
        mock_filter.return_value = mock_qs

        mock_user.created_pull_requests.exists.return_value = True
        mock_user.created_issues.exists.return_value = False
        mock_user.created_releases.exists.return_value = False

        assert calculator._type_diversity_score(mock_user) == 50


class TestConsistencyScore:
    """Tests for consistency score calculation."""

    def test_no_data(self, calculator, mock_user):
        """Test zero score with no contribution data."""
        mock_user.contribution_data = {}
        assert calculator._consistency_score(mock_user) == 0

    def test_all_active_days(self, calculator, mock_user):
        """Test full score when all days are active."""
        mock_user.contribution_data = {f"2025-01-{i:02d}": 1 for i in range(1, 31)}
        assert calculator._consistency_score(mock_user) == MAX_SCORE

    def test_partial_active_days(self, calculator, mock_user):
        """Test partial score with some inactive days."""
        data = {}
        for i in range(1, 11):
            data[f"2025-01-{i:02d}"] = 1
        for i in range(11, 21):
            data[f"2025-01-{i:02d}"] = 0
        mock_user.contribution_data = data
        assert math.isclose(calculator._consistency_score(mock_user), 50)


class TestFullCalculation:
    """Tests for end-to-end score calculation."""

    def test_zero_contributions_returns_zero(self, calculator, mock_user):
        """Test that a user with no data gets zero score."""
        with (
            patch.object(calculator, "_leadership_score", return_value=0),
            patch.object(calculator, "_breadth_score", return_value=0),
            patch.object(calculator, "_type_diversity_score", return_value=0),
        ):
            score = calculator.calculate(mock_user)
        assert score == 0

    def test_weighted_calculation(self, calculator, mock_user):
        """Test that the score is correctly weighted."""
        with (
            patch.object(calculator, "_contribution_score", return_value=80),
            patch.object(calculator, "_leadership_score", return_value=60),
            patch.object(calculator, "_recency_score", return_value=50),
            patch.object(calculator, "_breadth_score", return_value=40),
            patch.object(calculator, "_type_diversity_score", return_value=75),
            patch.object(calculator, "_consistency_score", return_value=30),
        ):
            score = calculator.calculate(mock_user)

        expected = round(
            WEIGHT_CONTRIBUTIONS * 80
            + WEIGHT_LEADERSHIP * 60
            + WEIGHT_RECENCY * 50
            + WEIGHT_BREADTH * 40
            + WEIGHT_TYPE_DIVERSITY * 75
            + WEIGHT_CONSISTENCY * 30,
            2,
        )
        assert score == expected

    def test_score_is_rounded(self, calculator, mock_user):
        """Test that the final score is rounded to 2 decimal places."""
        with (
            patch.object(calculator, "_contribution_score", return_value=33.333),
            patch.object(calculator, "_leadership_score", return_value=33.333),
            patch.object(calculator, "_recency_score", return_value=33.333),
            patch.object(calculator, "_breadth_score", return_value=33.333),
            patch.object(calculator, "_type_diversity_score", return_value=33.333),
            patch.object(calculator, "_consistency_score", return_value=33.333),
        ):
            score = calculator.calculate(mock_user)

        assert score == round(score, 2)
