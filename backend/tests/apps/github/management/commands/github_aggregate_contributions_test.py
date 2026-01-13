"""Test cases for github_aggregate_contributions management command."""

from datetime import UTC, datetime, timedelta
from unittest import mock

from apps.github.management.commands.github_aggregate_contributions import Command


class MockQuerySet:
    """Mock QuerySet that supports iteration and chaining without database access."""

    def __init__(self, items):
        self._items = items

    def __iter__(self):
        """Return iterator over items."""
        return iter(self._items)

    def filter(self, **kwargs):
        """Mock filter method."""
        return self

    def exists(self):
        """Mock exists method."""
        return len(self._items) > 0

    def count(self):
        """Return count of items."""
        return len(self._items)

    def iterator(self, chunk_size=None):
        """Mock iterator method."""
        return iter(self._items)

    def values(self, *fields):
        """Mock values method."""
        return self

    def annotate(self, **kwargs):
        """Mock annotate method."""
        return self


class TestAggregateContributionsCommand:
    """Test suite for github_aggregate_contributions management command."""

    def test_aggregate_user_contributions_empty(self):
        """Test aggregation with no contributions."""
        command = Command()
        mock_user = mock.Mock()
        mock_user.id = 1

        # Use fixed dates for testing
        fixed_now = datetime(2024, 1, 30, tzinfo=UTC)
        start_date = datetime(2024, 1, 1, tzinfo=UTC)

        with (
            mock.patch(
                "apps.github.management.commands.github_aggregate_contributions.Commit"
            ) as mock_commit,
            mock.patch(
                "apps.github.management.commands.github_aggregate_contributions.PullRequest"
            ) as mock_pr,
            mock.patch(
                "apps.github.management.commands.github_aggregate_contributions.Issue"
            ) as mock_issue,
            mock.patch(
                "apps.github.management.commands.github_aggregate_contributions.timezone.now"
            ) as mock_tz_now,
        ):
            # Mock timezone.now() to return a fixed date
            mock_tz_now.return_value = fixed_now

            # Mock empty querysets
            mock_commit.objects.filter.return_value = MockQuerySet([])
            mock_pr.objects.filter.return_value = MockQuerySet([])
            mock_issue.objects.filter.return_value = MockQuerySet([])

            result = command._aggregate_user_contributions(mock_user, start_date)

            # Should have 30 days of data (Jan 1 to Jan 30)
            assert isinstance(result, dict)
            assert len(result) == 30
            # All values should be 0
            assert all(count == 0 for count in result.values())

    def test_aggregate_user_contributions_with_data(self):
        """Test aggregation with contributions."""
        command = Command()
        mock_user = mock.Mock()
        mock_user.id = 1
        start_date = datetime(2024, 1, 1, tzinfo=UTC)

        with (
            mock.patch(
                "apps.github.management.commands.github_aggregate_contributions.Commit"
            ) as mock_commit,
            mock.patch(
                "apps.github.management.commands.github_aggregate_contributions.PullRequest"
            ) as mock_pr,
            mock.patch(
                "apps.github.management.commands.github_aggregate_contributions.Issue"
            ) as mock_issue,
            mock.patch(
                "apps.github.management.commands.github_aggregate_contributions.timezone"
            ) as mock_tz,
        ):
            # Mock timezone.now() to return a fixed date
            mock_tz.now.return_value = datetime(2024, 1, 5, tzinfo=UTC)

            # Mock querysets with data
            mock_commit.objects.filter.return_value = MockQuerySet(
                [
                    {"created_at": datetime(2024, 1, 1, 10, 0, tzinfo=UTC), "count": 2},
                    {"created_at": datetime(2024, 1, 2, 10, 0, tzinfo=UTC), "count": 1},
                ]
            )
            mock_pr.objects.filter.return_value = MockQuerySet(
                [{"created_at": datetime(2024, 1, 1, 11, 0, tzinfo=UTC), "count": 1}]
            )
            mock_issue.objects.filter.return_value = MockQuerySet(
                [{"created_at": datetime(2024, 1, 3, 12, 0, tzinfo=UTC), "count": 3}]
            )

            result = command._aggregate_user_contributions(mock_user, start_date)

            # Should have 5 days of data
            assert isinstance(result, dict)
            assert len(result) == 5
            # Check specific dates
            assert result["2024-01-01"] == 3  # 2 commits + 1 PR
            assert result["2024-01-02"] == 1  # 1 commit
            assert result["2024-01-03"] == 3  # 3 issues
            assert result["2024-01-04"] == 0
            assert result["2024-01-05"] == 0

    def test_handle_with_specific_user_found(self):
        """Test handle method with specific user that exists."""
        command = Command()
        command.stdout = mock.Mock()
        command.style = mock.Mock()
        command.style.ERROR = lambda x: x
        command.style.SUCCESS = lambda x: x

        mock_user = mock.Mock()
        mock_user.login = "testuser"
        mock_user.contribution_data = {}
        mock_user.save = mock.Mock()

        with (
            mock.patch(
                "apps.github.management.commands.github_aggregate_contributions.User"
            ) as mock_user_model,
            mock.patch.object(
                command, "_aggregate_user_contributions", return_value={"2024-01-01": 5}
            ),
        ):
            mock_queryset = MockQuerySet([mock_user])
            mock_user_model.objects.filter.return_value = mock_queryset

            command.handle(user="testuser", days=365, batch_size=100)

            assert mock_user.contribution_data == {"2024-01-01": 5}
            mock_user.save.assert_called_once_with(update_fields=["contribution_data"])

    def test_handle_with_specific_user_not_found(self):
        """Test handle method with specific user that doesn't exist."""
        command = Command()
        command.stdout = mock.Mock()
        command.style = mock.Mock()
        command.style.ERROR = lambda x: x
        command.style.SUCCESS = lambda x: x

        with mock.patch(
            "apps.github.management.commands.github_aggregate_contributions.User"
        ) as mock_user_model:
            mock_queryset = MockQuerySet([])
            mock_user_model.objects.filter.return_value = mock_queryset

            command.handle(user="nonexistent", days=365, batch_size=100)

            # Should write error message
            assert any("not found" in str(call) for call in command.stdout.write.call_args_list)

    def test_handle_all_users(self):
        """Test handle method processing all users."""
        command = Command()
        command.stdout = mock.Mock()
        command.style = mock.Mock()
        command.style.SUCCESS = lambda x: x

        mock_user1 = mock.Mock()
        mock_user1.login = "user1"
        mock_user1.contribution_data = {}
        mock_user1.save = mock.Mock()

        mock_user2 = mock.Mock()
        mock_user2.login = "user2"
        mock_user2.contribution_data = {}
        mock_user2.save = mock.Mock()

        with (
            mock.patch(
                "apps.github.management.commands.github_aggregate_contributions.User"
            ) as mock_user_model,
            mock.patch.object(
                command, "_aggregate_user_contributions", return_value={"2024-01-01": 5}
            ),
        ):
            mock_queryset = MockQuerySet([mock_user1, mock_user2])
            mock_user_model.objects.filter.return_value = mock_queryset

            command.handle(user=None, days=365, batch_size=100)

            # Both users should be saved
            assert mock_user1.save.call_count == 1
            assert mock_user2.save.call_count == 1
            # Both should have contribution data
            assert mock_user1.contribution_data == {"2024-01-01": 5}
            assert mock_user2.contribution_data == {"2024-01-01": 5}

    def test_handle_custom_days_parameter(self):
        """Test handle method with custom days parameter."""
        command = Command()
        command.stdout = mock.Mock()
        command.style = mock.Mock()
        command.style.SUCCESS = lambda x: x

        mock_user = mock.Mock()
        mock_user.contribution_data = {}
        mock_user.save = mock.Mock()

        with (
            mock.patch(
                "apps.github.management.commands.github_aggregate_contributions.User"
            ) as mock_user_model,
            mock.patch.object(
                command, "_aggregate_user_contributions", return_value={}
            ) as mock_aggregate,
            mock.patch(
                "apps.github.management.commands.github_aggregate_contributions.timezone"
            ) as mock_tz,
        ):
            mock_tz.now.return_value = datetime(2024, 1, 31, tzinfo=UTC)
            mock_queryset = MockQuerySet([mock_user])
            mock_user_model.objects.filter.return_value = mock_queryset

            command.handle(user=None, days=90, batch_size=100)

            # Verify aggregate was called
            assert mock_aggregate.called
            call_args = mock_aggregate.call_args[0]
            start_date = call_args[1]
            expected_start = datetime(2024, 1, 31, tzinfo=UTC) - timedelta(days=90)
            # Allow 1 second tolerance
            assert abs((expected_start - start_date).total_seconds()) < 1

    def test_contribution_data_date_format(self):
        """Test that contribution data uses correct date format."""
        command = Command()
        mock_user = mock.Mock()
        start_date = datetime(2024, 1, 1, tzinfo=UTC)

        with (
            mock.patch(
                "apps.github.management.commands.github_aggregate_contributions.Commit"
            ) as mock_commit,
            mock.patch(
                "apps.github.management.commands.github_aggregate_contributions.PullRequest"
            ) as mock_pr,
            mock.patch(
                "apps.github.management.commands.github_aggregate_contributions.Issue"
            ) as mock_issue,
            mock.patch(
                "apps.github.management.commands.github_aggregate_contributions.timezone"
            ) as mock_tz,
        ):
            mock_tz.now.return_value = datetime(2024, 1, 3, tzinfo=UTC)

            mock_commit.objects.filter.return_value = MockQuerySet([])
            mock_pr.objects.filter.return_value = MockQuerySet([])
            mock_issue.objects.filter.return_value = MockQuerySet([])

            result = command._aggregate_user_contributions(mock_user, start_date)

            # Verify all keys are in YYYY-MM-DD format
            for date_str in result:
                # Should not raise exception
                datetime.strptime(date_str, "%Y-%m-%d").astimezone(UTC)
                # Should match expected format
                assert len(date_str) == 10
                assert date_str[4] == "-"
                assert date_str[7] == "-"
