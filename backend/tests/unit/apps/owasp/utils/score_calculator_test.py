from datetime import UTC, date, datetime
from unittest.mock import ANY, MagicMock, call, patch

import pytest

from apps.github.models.user import User
from apps.owasp.exceptions import CertificateIssuanceError
from apps.owasp.models.crp.contribution_score import ContributionScore
from apps.owasp.models.crp.recognition_enums import EventTypeChoices, TierChoices
from apps.owasp.utils.score_calculator import ContributionScoreCalculator

CALCULATOR_PATH = "apps.owasp.utils.score_calculator"


class TestContributionScoreCalculator:
    """Test suite for ContributionScoreCalculator."""

    def _mock_recalculate_all_querysets(self, mock_user_class, mock_pr, mock_issue, users):
        """Set up mock querysets for User, PullRequest, and Issue for recalculate_all tests."""
        mock_users_qs = MagicMock()
        mock_users_qs.count.return_value = len(users)
        mock_users_qs.__iter__.return_value = iter(users)
        mock_users_qs.distinct.return_value.prefetch_related.return_value = mock_users_qs
        mock_user_class.objects.filter.return_value = mock_users_qs

        pr_chain = mock_pr.objects.filter.return_value.values.return_value.annotate.return_value
        pr_chain.values_list.return_value = []
        issue_chain = (
            mock_issue.objects.filter.return_value.values.return_value.annotate.return_value
        )
        issue_chain.values_list.return_value = []

    @patch(f"{CALCULATOR_PATH}.ScoringWeight")
    def test_load_scoring_weights(self, mock_scoring_weight):
        """Test load_scoring_weights retrieves active scoring weights from database."""
        w1 = MagicMock(event_type="pr_merged", score=20)
        w2 = MagicMock(event_type="pr_opened", score=5)
        mock_scoring_weight.objects.filter.return_value = [w1, w2]

        calc = ContributionScoreCalculator()

        mock_scoring_weight.objects.filter.assert_called_once_with(is_active=True)
        assert calc.scoring_weights == {"pr_merged": 20, "pr_opened": 5}

    @patch.object(
        ContributionScoreCalculator,
        "load_scoring_weights",
        return_value={"pr_merged": 20, "pr_opened": 5},
    )
    def test_calculate_score(self, mock_load):
        """Test calculate_score correctly computes breakdown and total score."""
        calc = ContributionScoreCalculator()
        counts = {"pr_merged": 3, "pr_opened": 2, "unknown_event": 5}

        total_score, breakdown = calc.calculate_score(counts)

        assert total_score == 70  # (3 * 20) + (2 * 5) + (5 * 0)
        assert breakdown == {"pr_merged": 60, "pr_opened": 10, "unknown_event": 0}

    @patch.object(
        ContributionScoreCalculator,
        "load_scoring_weights",
        return_value={"pr_merged": 20},
    )
    @patch.object(ContributionScoreCalculator, "get_contribution_breakdown")
    def test_calculate(self, mock_breakdown, mock_load):
        """Test calculate delegates to get_contribution_breakdown and sums the result."""
        user = User(login="test_user")
        mock_breakdown.return_value = {"pr_merged": 40, "issue_completed": 10}

        calc = ContributionScoreCalculator()
        start = date(2026, 1, 1)
        end = date(2026, 6, 1)
        total, breakdown = calc.calculate(user, start_date=start, end_date=end)

        assert total == 50
        assert breakdown == {"pr_merged": 40, "issue_completed": 10}
        mock_breakdown.assert_called_once_with(user, start, end)

    @pytest.mark.parametrize(
        ("score", "expected_tier"),
        [
            (600, "level_4"),
            (500, "level_4"),
            (300, "level_3"),
            (250, "level_3"),
            (150, "level_2"),
            (100, "level_2"),
            (50, "level_1"),
            (0, "level_1"),
        ],
    )
    @patch.object(ContributionScoreCalculator, "load_scoring_weights", return_value={})
    def test_get_tier(self, mock_load, score, expected_tier):
        """Test get_tier maps score thresholds to tier strings."""
        calc = ContributionScoreCalculator()
        assert calc.get_tier(score) == expected_tier

    @patch.object(ContributionScoreCalculator, "load_scoring_weights", return_value={})
    def test_get_tier_negative_score(self, mock_load):
        """Test get_tier returns level_1 for negative scores."""
        calc = ContributionScoreCalculator()
        assert calc.get_tier(-10) == "level_1"

    @patch.object(ContributionScoreCalculator, "load_scoring_weights", return_value={})
    @patch(f"{CALCULATOR_PATH}.PullRequest")
    def test_count_merged_pull_requests(self, mock_pr, mock_load):
        """Test count_merged_pull_requests with and without date range."""
        user = User(login="test_user")
        mock_qs = MagicMock()
        mock_pr.objects.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.count.return_value = 5

        calc = ContributionScoreCalculator()

        # Without date range
        count = calc.count_merged_pull_requests(user)
        assert count == 5
        mock_pr.objects.filter.assert_called_once_with(
            author=user,
            merged_at__isnull=False,
            repository__is_fork=False,
            repository__organization__is_owasp_related_organization=True,
        )

        mock_qs.filter.assert_not_called()

        # With date range
        start = date(2026, 1, 1)
        end = date(2026, 2, 1)
        calc.count_merged_pull_requests(user, start_date=start, end_date=end)
        assert mock_qs.filter.call_args_list == [
            call(merged_at__date__gte=start),
            call(merged_at__date__lte=end),
        ]

    @patch.object(ContributionScoreCalculator, "load_scoring_weights", return_value={})
    @patch(f"{CALCULATOR_PATH}.PullRequest")
    def test_count_opened_pull_requests(self, mock_pr, mock_load):
        """Test count_opened_pull_requests with and without date range."""
        user = User(login="test_user")
        mock_qs = MagicMock()
        mock_pr.objects.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.count.return_value = 3

        calc = ContributionScoreCalculator()

        # Without date range
        count = calc.count_opened_pull_requests(user)
        assert count == 3
        mock_pr.objects.filter.assert_called_once_with(
            author=user,
            repository__is_fork=False,
            repository__organization__is_owasp_related_organization=True,
        )
        mock_qs.filter.assert_not_called()

        # With date range
        start = date(2026, 1, 1)
        end = date(2026, 2, 1)
        calc.count_opened_pull_requests(user, start_date=start, end_date=end)
        assert mock_qs.filter.call_args_list == [
            call(created_at__date__gte=start),
            call(created_at__date__lte=end),
        ]

    @patch.object(ContributionScoreCalculator, "load_scoring_weights", return_value={})
    @patch(f"{CALCULATOR_PATH}.Issue")
    def test_count_completed_issues(self, mock_issue, mock_load):
        """Test count_completed_issues with and without date range."""
        user = User(login="test_user")
        mock_qs = MagicMock()
        mock_issue.objects.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.count.return_value = 4

        calc = ContributionScoreCalculator()

        # Without date range
        count = calc.count_completed_issues(user)
        assert count == 4
        mock_issue.objects.filter.assert_called_once_with(
            author=user,
            state_reason=mock_issue.StateReason.COMPLETED,
            repository__is_fork=False,
            repository__organization__is_owasp_related_organization=True,
        )
        mock_qs.filter.assert_not_called()

        # With date range
        start = date(2026, 1, 1)
        end = date(2026, 2, 1)
        calc.count_completed_issues(user, start_date=start, end_date=end)
        assert mock_qs.filter.call_args_list == [
            call(created_at__date__gte=start),
            call(created_at__date__lte=end),
        ]

    @pytest.mark.parametrize(
        ("method_name", "model_name", "date_field"),
        [
            ("count_merged_pull_requests", "PullRequest", "merged_at"),
            ("count_opened_pull_requests", "PullRequest", "created_at"),
            ("count_completed_issues", "Issue", "created_at"),
        ],
    )
    @patch.object(ContributionScoreCalculator, "load_scoring_weights", return_value={})
    def test_counters_apply_single_date_bound(
        self, mock_load, method_name, model_name, date_field
    ):
        """Test each counter applies only the date bound that was supplied."""
        user = User(login="test_user")
        start = date(2026, 3, 1)
        end = date(2026, 4, 1)

        with patch(f"{CALCULATOR_PATH}.{model_name}") as mock_model:
            mock_qs = MagicMock()
            mock_model.objects.filter.return_value = mock_qs
            mock_qs.filter.return_value = mock_qs

            calc = ContributionScoreCalculator()
            getattr(calc, method_name)(user, start_date=start)
            mock_qs.filter.assert_called_once_with(**{f"{date_field}__date__gte": start})

            mock_qs.filter.reset_mock()
            getattr(calc, method_name)(user, end_date=end)
            mock_qs.filter.assert_called_once_with(**{f"{date_field}__date__lte": end})

    @patch.object(ContributionScoreCalculator, "load_scoring_weights", return_value={})
    @patch.object(ContributionScoreCalculator, "count_merged_pull_requests", return_value=2)
    @patch.object(ContributionScoreCalculator, "count_opened_pull_requests", return_value=1)
    @patch.object(ContributionScoreCalculator, "count_completed_issues", return_value=3)
    @patch.object(
        ContributionScoreCalculator,
        "calculate_score",
        return_value=(100, {"pr_merged": 40}),
    )
    def test_get_contribution_breakdown(
        self, mock_calc_score, mock_issues, mock_opened, mock_merged, mock_load
    ):
        """Test get_contribution_breakdown gathers counts and calls calculate_score."""
        user = User(login="test_user")
        calc = ContributionScoreCalculator()

        breakdown = calc.get_contribution_breakdown(user)

        assert breakdown == {"pr_merged": 40}
        mock_calc_score.assert_called_once_with(
            {"pr_merged": 2, "pr_opened": 1, "issue_completed": 3}
        )

    @patch.object(ContributionScoreCalculator, "load_scoring_weights", return_value={})
    @patch.object(ContributionScoreCalculator, "count_merged_pull_requests", return_value=0)
    @patch.object(ContributionScoreCalculator, "count_opened_pull_requests", return_value=0)
    @patch.object(ContributionScoreCalculator, "count_completed_issues", return_value=0)
    def test_contribution_breakdown_uses_event_type_choices(
        self, mock_issues, mock_opened, mock_merged, mock_load
    ):
        """Test breakdown keys match the scoring weight event types."""
        calc = ContributionScoreCalculator()

        breakdown = calc.get_contribution_breakdown(User(login="test_user"))

        assert set(breakdown) == set(EventTypeChoices.values)

    @patch("django.db.transaction.Atomic.__enter__", return_value=None)
    @patch("django.db.transaction.Atomic.__exit__", return_value=None)
    @patch.object(
        ContributionScoreCalculator,
        "load_scoring_weights",
        return_value={"pr_merged": 50},
    )
    @patch(f"{CALCULATOR_PATH}.Certificate")
    @patch(f"{CALCULATOR_PATH}.BulkSaveModel")
    @patch(f"{CALCULATOR_PATH}.User")
    @patch(f"{CALCULATOR_PATH}.Issue")
    @patch(f"{CALCULATOR_PATH}.PullRequest")
    def test_recalculate_all_updates_and_creates_scores(
        self,
        mock_pr,
        mock_issue,
        mock_user_class,
        mock_bulk_save_model,
        mock_cert_class,
        mock_load,
        mock_exit,
        mock_enter,
    ):
        """Test recalculate_all processes users, updates/creates scores, and issues certs."""
        user1 = User(login="user1")
        existing_score = ContributionScore(github_user=user1, value=10, tier="level_1")
        user1.contribution_score = existing_score
        user2 = User(login="user2")

        self._mock_recalculate_all_querysets(mock_user_class, mock_pr, mock_issue, [user1, user2])
        now = datetime(2026, 11, 1, tzinfo=UTC)

        calc = ContributionScoreCalculator()
        with patch(f"{CALCULATOR_PATH}.timezone.now", return_value=now):
            res = calc.recalculate_all()

        assert res["total"] == 2
        assert res["created"] == 1
        assert res["updated"] == 1
        assert res["failed_count"] == 0

        users_filter = mock_user_class.objects.filter.call_args.args[0]
        assert ("contribution_score__isnull", False) in users_filter.children
        assert existing_score.nest_updated_at == now
        mock_bulk_save_model.bulk_save.assert_called_once_with(
            ContributionScore, ANY, fields=["value", "tier", "nest_updated_at"]
        )
        assert mock_cert_class.issue_certificate.call_count == 2

    @patch("django.db.transaction.Atomic.__enter__", return_value=None)
    @patch("django.db.transaction.Atomic.__exit__", return_value=None)
    @patch.object(
        ContributionScoreCalculator,
        "load_scoring_weights",
        return_value={"pr_merged": 50},
    )
    @patch(f"{CALCULATOR_PATH}.Certificate")
    @patch(f"{CALCULATOR_PATH}.BulkSaveModel")
    @patch(f"{CALCULATOR_PATH}.User")
    @patch(f"{CALCULATOR_PATH}.Issue")
    @patch(f"{CALCULATOR_PATH}.PullRequest")
    def test_recalculate_all_batching(
        self,
        mock_pr,
        mock_issue,
        mock_user_class,
        mock_bulk_save_model,
        mock_cert_class,
        mock_load,
        mock_exit,
        mock_enter,
    ):
        """Test recalculate_all bulk saves when batch size limit is reached."""
        user1 = User(login="batch_user1")
        user2 = User(login="batch_user2")

        self._mock_recalculate_all_querysets(mock_user_class, mock_pr, mock_issue, [user1, user2])

        calc = ContributionScoreCalculator()
        calc.BATCH_SIZE = 2
        res = calc.recalculate_all()

        assert res["total"] == 2
        assert res["created"] == 2
        mock_bulk_save_model.bulk_save.assert_called_once_with(
            ContributionScore, ANY, fields=["value", "tier", "nest_updated_at"]
        )
        assert mock_cert_class.issue_certificate.call_count == 2

    @patch("django.db.transaction.Atomic.__enter__", return_value=None)
    @patch("django.db.transaction.Atomic.__exit__", return_value=None)
    @patch.object(
        ContributionScoreCalculator,
        "load_scoring_weights",
        return_value={"pr_merged": 50},
    )
    @patch(f"{CALCULATOR_PATH}.Certificate")
    @patch(f"{CALCULATOR_PATH}.BulkSaveModel")
    @patch(f"{CALCULATOR_PATH}.User")
    @patch(f"{CALCULATOR_PATH}.Issue")
    @patch(f"{CALCULATOR_PATH}.PullRequest")
    def test_recalculate_all_batching_certificate_failures(
        self,
        mock_pr,
        mock_issue,
        mock_user_class,
        mock_bulk_save_model,
        mock_cert_class,
        mock_load,
        mock_exit,
        mock_enter,
    ):
        """Test recalculate_all error handling when batch size limit is reached."""
        user1 = User(login="batch_fail1")
        user2 = User(login="batch_fail2")

        self._mock_recalculate_all_querysets(mock_user_class, mock_pr, mock_issue, [user1, user2])

        mock_cert_class.issue_certificate.side_effect = [
            CertificateIssuanceError("Batch issue 1"),
            CertificateIssuanceError("Batch issue 2"),
        ]

        calc = ContributionScoreCalculator()
        calc.BATCH_SIZE = 1
        res = calc.recalculate_all()

        assert res["total"] == 2
        assert res["failed_count"] == 2
        assert res["failures"][0][0] == "batch_fail1"
        assert res["failures"][1][0] == "batch_fail2"

    @patch("django.db.transaction.Atomic.__enter__", return_value=None)
    @patch("django.db.transaction.Atomic.__exit__", return_value=None)
    @patch.object(
        ContributionScoreCalculator,
        "load_scoring_weights",
        return_value={"pr_merged": 50},
    )
    @patch(f"{CALCULATOR_PATH}.Certificate")
    @patch(f"{CALCULATOR_PATH}.BulkSaveModel")
    @patch(f"{CALCULATOR_PATH}.User")
    @patch(f"{CALCULATOR_PATH}.Issue")
    @patch(f"{CALCULATOR_PATH}.PullRequest")
    def test_recalculate_all_final_batch_unexpected_certificate_error(
        self,
        mock_pr,
        mock_issue,
        mock_user_class,
        mock_bulk_save_model,
        mock_cert_class,
        mock_load,
        mock_exit,
        mock_enter,
    ):
        """Test an unexpected error in the final partial batch is recorded, not raised."""
        users = [User(login=f"partial_user{i}") for i in range(3)]

        self._mock_recalculate_all_querysets(mock_user_class, mock_pr, mock_issue, users)

        unexpected_error = RuntimeError("Provider crashed")
        mock_cert_class.issue_certificate.side_effect = [None, None, unexpected_error]

        calc = ContributionScoreCalculator()
        calc.BATCH_SIZE = 2
        res = calc.recalculate_all()

        # One full batch of two users followed by a final partial batch of one user.
        assert mock_bulk_save_model.bulk_save.call_count == 2
        assert mock_bulk_save_model.bulk_save.call_args_list == [
            call(ContributionScore, ANY, fields=["value", "tier", "nest_updated_at"]),
            call(ContributionScore, ANY, fields=["value", "tier", "nest_updated_at"]),
        ]
        assert mock_cert_class.issue_certificate.call_count == 3
        assert res["total"] == 3
        assert res["created"] == 3
        assert res["failed_count"] == 1
        assert res["failures"] == [("partial_user2", unexpected_error)]

    @patch.object(
        ContributionScoreCalculator,
        "load_scoring_weights",
        return_value={"pr_merged": 50},
    )
    @patch(f"{CALCULATOR_PATH}.Certificate")
    @patch(f"{CALCULATOR_PATH}.BulkSaveModel")
    @patch(f"{CALCULATOR_PATH}.User")
    @patch(f"{CALCULATOR_PATH}.Issue")
    @patch(f"{CALCULATOR_PATH}.PullRequest")
    def test_recalculate_all_no_users(
        self,
        mock_pr,
        mock_issue,
        mock_user_class,
        mock_bulk_save_model,
        mock_cert_class,
        mock_load,
    ):
        """Test recalculate_all when no users have contributions."""
        self._mock_recalculate_all_querysets(mock_user_class, mock_pr, mock_issue, [])

        calc = ContributionScoreCalculator()
        res = calc.recalculate_all()

        assert res["total"] == 0
        assert res["created"] == 0
        assert res["updated"] == 0
        mock_bulk_save_model.bulk_save.assert_not_called()
        mock_cert_class.issue_certificate.assert_not_called()

    @patch("django.db.transaction.Atomic.__enter__", return_value=None)
    @patch("django.db.transaction.Atomic.__exit__", return_value=None)
    @patch.object(
        ContributionScoreCalculator,
        "load_scoring_weights",
        return_value={"pr_merged": 50},
    )
    @patch(f"{CALCULATOR_PATH}.Certificate")
    @patch(f"{CALCULATOR_PATH}.BulkSaveModel")
    @patch(f"{CALCULATOR_PATH}.User")
    @patch(f"{CALCULATOR_PATH}.Issue")
    @patch(f"{CALCULATOR_PATH}.PullRequest")
    def test_recalculate_all_handles_certificate_failures(
        self,
        mock_pr,
        mock_issue,
        mock_user_class,
        mock_bulk_save_model,
        mock_cert_class,
        mock_load,
        mock_exit,
        mock_enter,
    ):
        """Test recalculate_all records certificate issuance errors."""
        user1 = User(login="failing_user")
        existing_score = ContributionScore(github_user=user1, value=10, tier="level_1")
        user1.contribution_score = existing_score

        self._mock_recalculate_all_querysets(mock_user_class, mock_pr, mock_issue, [user1])

        mock_cert_class.issue_certificate.side_effect = CertificateIssuanceError("Issuance failed")

        calc = ContributionScoreCalculator()
        res = calc.recalculate_all()

        assert res["total"] == 1
        assert res["failed_count"] == 1
        assert res["failures"][0][0] == "failing_user"

    @patch("django.db.transaction.Atomic.__enter__", return_value=None)
    @patch("django.db.transaction.Atomic.__exit__", return_value=None)
    @patch.object(
        ContributionScoreCalculator,
        "load_scoring_weights",
        return_value={"pr_merged": 50},
    )
    @patch(f"{CALCULATOR_PATH}.Certificate")
    @patch(f"{CALCULATOR_PATH}.ContributionScore.objects")
    def test_recalculate_user(
        self, mock_contrib_score_objects, mock_cert_class, mock_load, mock_exit, mock_enter
    ):
        """Test recalculate_user for a single user."""
        user = User(login="single_user")

        calc = ContributionScoreCalculator()
        with patch.object(calc, "calculate", return_value=(150, {"pr_merged": 150})):
            mock_contrib_score_objects.update_or_create.return_value = (MagicMock(), True)

            result = calc.recalculate_user(user)

            assert result == {
                "total_score": 150,
                "tier": "level_2",
                "created": True,
            }
            mock_contrib_score_objects.update_or_create.assert_called_once_with(
                github_user=user,
                defaults={"value": 150, "tier": "level_2"},
            )
            mock_cert_class.issue_certificate.assert_called_once_with(
                user, 150, TierChoices.LEVEL_2
            )
