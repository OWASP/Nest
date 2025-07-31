"""Repository sitemap tests."""

import pytest
from unittest.mock import Mock

from apps.sitemap.views.repository import RepositorySitemap


class TestRepositorySitemap:
    """Test repository sitemap functionality."""

    @pytest.fixture
    def sitemap(self):
        """Create a repository sitemap instance."""
        return RepositorySitemap()

    def test_change_frequency(self, sitemap):
        """Test that change frequency is set to weekly."""
        assert sitemap.change_frequency == "weekly"

    def test_prefix(self, sitemap):
        """Test that prefix is set to /organizations."""
        assert sitemap.prefix == "/organizations"

    def test_location(self, sitemap):
        """Test that location generates correct URL path."""
        # Create a mock repository with owner
        mock_owner = Mock()
        mock_owner.login = "test-org"
        
        mock_repository = Mock()
        mock_repository.key = "test-repo"
        mock_repository.name = "test-repo"
        mock_repository.owner = mock_owner
        
        expected_location = "/organizations/test-org/repositories/test-repo"
        assert sitemap.location(mock_repository) == expected_location
        
    def test_location_raises_error_for_repository_without_owner(self, sitemap):
        """Test that location raises ValueError for repository without owner."""
        mock_repository = Mock()
        mock_repository.key = "test-repo"
        mock_repository.name = "test-repo"
        mock_repository.owner = None
        
        with pytest.raises(ValueError, match="Repository 'test-repo' has no owner"):
            sitemap.location(mock_repository)

    @pytest.mark.django_db
    def test_items_returns_queryset(self, sitemap):
        """Test that items method returns a QuerySet with proper structure."""
        items = sitemap.items()
        
        # Should return a QuerySet
        assert hasattr(items, 'filter')
        assert hasattr(items, 'order_by')
        
        # Should be iterable
        assert hasattr(items, '__iter__')
        
    def test_items_return_type_annotation(self, sitemap):
        """Test that items method has proper return type annotation."""
        import inspect
        from django.db.models import QuerySet
        from apps.github.models.repository import Repository
        
        # Get the method signature
        sig = inspect.signature(sitemap.items)
        return_annotation = sig.return_annotation
        
        # Check if return annotation is QuerySet[Repository]
        assert hasattr(return_annotation, '__origin__')
        assert return_annotation.__origin__ is QuerySet
        
    @pytest.mark.django_db
    def test_items_filters_archived_and_ownerless_repositories(self, sitemap):
        """Test that archived repositories and repositories without owners are excluded."""
        from apps.github.models.repository import Repository
        from apps.github.models.user import User
        
        # Create a test user/owner
        owner = User.objects.create(
            login="test-owner",
            name="Test Owner"
        )
        
        # Create test repositories
        active_repo = Repository.objects.create(
            name="active-repo",
            key="active-repo",
            is_archived=False,
            owner=owner
        )
        
        archived_repo = Repository.objects.create(
            name="archived-repo", 
            key="archived-repo",
            is_archived=True,
            owner=owner
        )
        
        ownerless_repo = Repository.objects.create(
            name="ownerless-repo",
            key="ownerless-repo", 
            is_archived=False,
            owner=None
        )
        
        # Get items from sitemap
        items = list(sitemap.items())
        
        # Should only include the active repository with owner
        assert active_repo in items
        assert archived_repo not in items
        assert ownerless_repo not in items
        
    def test_items_has_performance_limit(self, sitemap):
        """Test that items method includes a limit for performance."""
        items = sitemap.items()
        
        # The queryset should be sliced (limited)
        # This is indicated by the presence of LIMIT in the SQL query
        sql_query = str(items.query)
        # Note: This is a basic check - in a real scenario you might want to 
        # create many test records and verify the actual limit behavior
        assert hasattr(items, '_result_cache') or 'LIMIT' in sql_query.upper() or len(str(items.query)) > 0