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
        assert "total_contributions" in field_names
