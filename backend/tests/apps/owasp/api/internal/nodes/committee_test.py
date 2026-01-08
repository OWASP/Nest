"""Tests for Committee GraphQL node."""

import math
from unittest.mock import Mock

from apps.owasp.api.internal.nodes.committee import CommitteeNode
from tests.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestCommitteeNode(GraphQLNodeBaseTest):
    def test_contributors_count_resolver(self):
        """Test contributors_count returns count from repository."""
        mock_repo = Mock()
        mock_repo.contributors_count = 42

        mock_committee = Mock()
        mock_committee.owasp_repository = mock_repo

        field = self._get_field_by_name("contributors_count", CommitteeNode)
        result = field.base_resolver.wrapped_func(mock_committee)

        assert result == 42

    def test_created_at_resolver(self):
        """Test created_at returns indexed timestamp."""
        mock_committee = Mock()
        mock_committee.idx_created_at = 1234567890.0

        field = self._get_field_by_name("created_at", CommitteeNode)
        result = field.base_resolver.wrapped_func(mock_committee)

        assert math.isclose(result, 1234567890.0)

    def test_forks_count_resolver(self):
        """Test forks_count returns count from repository."""
        mock_repo = Mock()
        mock_repo.forks_count = 15

        mock_committee = Mock()
        mock_committee.owasp_repository = mock_repo

        field = self._get_field_by_name("forks_count", CommitteeNode)
        result = field.base_resolver.wrapped_func(mock_committee)

        assert result == 15

    def test_issues_count_resolver(self):
        """Test issues_count returns open issues from repository."""
        mock_repo = Mock()
        mock_repo.open_issues_count = 23

        mock_committee = Mock()
        mock_committee.owasp_repository = mock_repo

        field = self._get_field_by_name("issues_count", CommitteeNode)
        result = field.base_resolver.wrapped_func(mock_committee)

        assert result == 23

    def test_repositories_count_resolver(self):
        """Test repositories_count always returns 1 for committees."""
        mock_committee = Mock()

        field = self._get_field_by_name("repositories_count", CommitteeNode)
        result = field.base_resolver.wrapped_func(mock_committee)

        assert result == 1

    def test_stars_count_resolver(self):
        """Test stars_count returns count from repository."""
        mock_repo = Mock()
        mock_repo.stars_count = 100

        mock_committee = Mock()
        mock_committee.owasp_repository = mock_repo

        field = self._get_field_by_name("stars_count", CommitteeNode)
        result = field.base_resolver.wrapped_func(mock_committee)

        assert result == 100
