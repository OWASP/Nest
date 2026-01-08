"""Tests for MemberSnapshot GraphQL queries."""

from unittest.mock import Mock, patch

from apps.owasp.api.internal.queries.member_snapshot import MemberSnapshotQuery


class TestMemberSnapshotQuery:
    def test_member_snapshot_user_not_found(self):
        from apps.github.models.user import User

        query = MemberSnapshotQuery()

        with patch("apps.owasp.api.internal.queries.member_snapshot.User.objects.get") as mock_get:
            mock_get.side_effect = User.DoesNotExist

            result = query.member_snapshot(user_login="nonexistent")

            assert result is None

    def test_member_snapshot_by_user_and_year(self):
        query = MemberSnapshotQuery()

        mock_user = Mock()
        mock_snapshot = Mock()

        with (
            patch("apps.owasp.api.internal.queries.member_snapshot.User") as mock_user_cls,
            patch(
                "apps.owasp.api.internal.queries.member_snapshot.MemberSnapshot"
            ) as mock_snapshot_cls,
        ):
            mock_user_cls.objects.get.return_value = mock_user

            mock_queryset = Mock()
            mock_queryset.select_related.return_value = mock_queryset
            mock_queryset.prefetch_related.return_value = mock_queryset
            mock_queryset.filter.return_value = mock_queryset
            mock_queryset.order_by.return_value = mock_queryset
            mock_queryset.first.return_value = mock_snapshot

            mock_snapshot_cls.objects = mock_queryset

            result = query.member_snapshot(user_login="testuser", start_year=2025)

            mock_user_cls.objects.get.assert_called_once_with(login="testuser")
            # select_related and prefetch_related are called, then filter twice
            mock_queryset.select_related.assert_called_once()
            mock_queryset.prefetch_related.assert_called_once()
            assert mock_queryset.filter.call_count == 2
            assert result == mock_snapshot

    def test_member_snapshots_all(self):
        query = MemberSnapshotQuery()

        mock_snapshots = [Mock(), Mock()]

        with patch(
            "apps.owasp.api.internal.queries.member_snapshot.MemberSnapshot"
        ) as mock_snapshot_cls:
            mock_queryset = Mock()
            mock_queryset.order_by.return_value = mock_queryset
            mock_queryset.__getitem__ = Mock(return_value=mock_snapshots)

            mock_snapshot_cls.objects.all.return_value = mock_queryset

            result = query.member_snapshots(limit=10)

            mock_snapshot_cls.objects.all.assert_called_once()
            mock_queryset.order_by.assert_called_once_with("-start_at")
            mock_queryset.__getitem__.assert_called_once_with(slice(None, 10, None))
            assert result == mock_snapshots

    def test_member_snapshots_by_user(self):
        query = MemberSnapshotQuery()

        mock_user = Mock()
        mock_snapshots = [Mock()]

        with (
            patch("apps.owasp.api.internal.queries.member_snapshot.User") as mock_user_cls,
            patch(
                "apps.owasp.api.internal.queries.member_snapshot.MemberSnapshot"
            ) as mock_snapshot_cls,
        ):
            mock_user_cls.objects.get.return_value = mock_user

            mock_queryset = Mock()
            mock_queryset.filter.return_value = mock_queryset
            mock_queryset.order_by.return_value = mock_queryset
            mock_queryset.__getitem__ = Mock(return_value=mock_snapshots)

            mock_snapshot_cls.objects.all.return_value = mock_queryset

            result = query.member_snapshots(user_login="testuser", limit=5)

            mock_user_cls.objects.get.assert_called_once_with(login="testuser")
            mock_queryset.filter.assert_called_once_with(github_user=mock_user)
            assert result == mock_snapshots

    def test_member_snapshots_user_not_found_returns_empty(self):
        from apps.github.models.user import User

        query = MemberSnapshotQuery()

        with patch("apps.owasp.api.internal.queries.member_snapshot.User.objects.get") as mock_get:
            mock_get.side_effect = User.DoesNotExist

            result = query.member_snapshots(user_login="nonexistent")

            assert result == []
