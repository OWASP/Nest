"""Tests for MemberSnapshot GraphQL node."""

from unittest.mock import Mock

from apps.owasp.api.internal.nodes.member_snapshot import MemberSnapshotNode


class TestMemberSnapshotNode:
    def test_node_fields(self):
        mock_snapshot = Mock()
        mock_snapshot.start_at = "2025-01-01"
        mock_snapshot.end_at = "2025-10-01"
        mock_snapshot.contribution_heatmap_data = {"2025-01-15": 5}

        node = MemberSnapshotNode.__strawberry_definition__

        field_names = {field.name for field in node.fields}

        assert "start_at" in field_names
        assert "end_at" in field_names
        assert "contribution_heatmap_data" in field_names
        assert "github_user" in field_names
        assert "commits_count" in field_names
        assert "pull_requests_count" in field_names
        assert "issues_count" in field_names
        assert "messages_count" in field_names
        assert "total_contributions" in field_names

    def test_commits_count_resolver(self):
        """Test commits_count returns count from snapshot."""
        mock_snapshot = Mock()
        mock_snapshot.commits_count = 42

        result = MemberSnapshotNode.commits_count(mock_snapshot)

        assert result == 42

    def test_github_user_resolver(self):
        """Test github_user returns user from snapshot."""
        mock_user = Mock()
        mock_snapshot = Mock()
        mock_snapshot.github_user = mock_user

        result = MemberSnapshotNode.github_user(mock_snapshot)

        assert result == mock_user

    def test_issues_count_resolver(self):
        """Test issues_count returns count from snapshot."""
        mock_snapshot = Mock()
        mock_snapshot.issues_count = 15

        result = MemberSnapshotNode.issues_count(mock_snapshot)

        assert result == 15

    def test_pull_requests_count_resolver(self):
        """Test pull_requests_count returns count from snapshot."""
        mock_snapshot = Mock()
        mock_snapshot.pull_requests_count = 23

        result = MemberSnapshotNode.pull_requests_count(mock_snapshot)

        assert result == 23

    def test_messages_count_resolver(self):
        """Test messages_count returns count from snapshot."""
        mock_snapshot = Mock()
        mock_snapshot.messages_count = 100

        result = MemberSnapshotNode.messages_count(mock_snapshot)

        assert result == 100

    def test_total_contributions_resolver(self):
        """Test total_contributions returns total from snapshot."""
        mock_snapshot = Mock()
        mock_snapshot.total_contributions = 80

        result = MemberSnapshotNode.total_contributions(mock_snapshot)

        assert result == 80
