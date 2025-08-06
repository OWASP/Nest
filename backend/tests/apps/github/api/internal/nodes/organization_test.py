"""Test cases for OrganizationNode."""

from unittest.mock import Mock, patch

from apps.github.api.internal.nodes.organization import (
    OrganizationNode,
    OrganizationStatsNode,
)


class TestOrganizationNode:
    def test_organization_node_inheritance(self):
        assert hasattr(OrganizationNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        field_names = {field.name for field in OrganizationNode.__strawberry_definition__.fields}
        expected_field_names = {
            "avatar_url",
            "collaborators_count",
            "company",
            "created_at",
            "description",
            "email",
            "followers_count",
            "location",
            "login",
            "name",
            "stats",
            "updated_at",
            "url",
        }
        assert field_names == expected_field_names

    def test_resolve_stats(self):
        stats_field = next(
            (f for f in OrganizationNode.__strawberry_definition__.fields if f.name == "stats"),
            None,
        )
        assert stats_field is not None
        assert stats_field.type is OrganizationStatsNode

    def test_resolve_url(self):
        url_field = next(
            (f for f in OrganizationNode.__strawberry_definition__.fields if f.name == "url"), None
        )
        assert url_field is not None
        assert url_field.type is str

    @patch("apps.github.models.repository.Repository.objects")
    @patch("apps.github.models.repository_contributor.RepositoryContributor.objects")
    def test_stats_method_with_data(self, mock_repo_contributor_objects, mock_repository_objects):
        """Test stats method with actual data."""
        # Mock repository queryset
        mock_repositories = Mock()
        mock_repositories.count.return_value = 5
        mock_repositories.aggregate.return_value = {
            "total_stars": 100,
            "total_forks": 50,
            "total_issues": 25,
        }
        mock_repository_objects.filter.return_value = mock_repositories

        # Mock repository contributor queryset
        mock_contributors = Mock()
        mock_contributors.values.return_value.distinct.return_value.count.return_value = 15
        mock_repo_contributor_objects.filter.return_value = mock_contributors

        # Create mock organization
        mock_organization = Mock()

        # Call stats method
        result = OrganizationNode.stats(mock_organization)

        # Verify result
        assert isinstance(result, OrganizationStatsNode)
        assert result.total_repositories == 5
        assert result.total_contributors == 15
        assert result.total_stars == 100
        assert result.total_forks == 50
        assert result.total_issues == 25

    @patch("apps.github.models.repository.Repository.objects")
    @patch("apps.github.models.repository_contributor.RepositoryContributor.objects")
    def test_stats_method_with_none_values(
        self, mock_repo_contributor_objects, mock_repository_objects
    ):
        """Test stats method when aggregate returns None values."""
        # Mock repository queryset
        mock_repositories = Mock()
        mock_repositories.count.return_value = 3
        mock_repositories.aggregate.return_value = {
            "total_stars": None,
            "total_forks": None,
            "total_issues": None,
        }
        mock_repository_objects.filter.return_value = mock_repositories

        # Mock repository contributor queryset
        mock_contributors = Mock()
        mock_contributors.values.return_value.distinct.return_value.count.return_value = 8
        mock_repo_contributor_objects.filter.return_value = mock_contributors

        # Create mock organization
        mock_organization = Mock()

        # Call stats method
        result = OrganizationNode.stats(mock_organization)

        # Verify result with default values
        assert isinstance(result, OrganizationStatsNode)
        assert result.total_repositories == 3
        assert result.total_contributors == 8
        assert result.total_stars == 0
        assert result.total_forks == 0
        assert result.total_issues == 0

    def test_url_method(self):
        """Test url method."""
        mock_organization = Mock()
        mock_organization.url = "https://github.com/test-org"

        result = OrganizationNode.url(mock_organization)
        assert result == "https://github.com/test-org"


class TestOrganizationStatsNode:
    def test_organization_stats_node(self):
        expected_fields = {
            "total_contributors",
            "total_forks",
            "total_issues",
            "total_repositories",
            "total_stars",
        }
        field_names = {
            field.name for field in OrganizationStatsNode.__strawberry_definition__.fields
        }
        assert field_names == expected_fields

    def test_organization_stats_node_creation(self):
        """Test creating OrganizationStatsNode with values."""
        stats = OrganizationStatsNode(
            total_repositories=10,
            total_contributors=25,
            total_stars=150,
            total_forks=75,
            total_issues=30,
        )

        assert stats.total_repositories == 10
        assert stats.total_contributors == 25
        assert stats.total_stars == 150
        assert stats.total_forks == 75
        assert stats.total_issues == 30
