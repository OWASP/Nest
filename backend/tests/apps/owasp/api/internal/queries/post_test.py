"""Test cases for PostQuery."""

from unittest.mock import Mock, patch

from apps.owasp.api.internal.queries.post import PostQuery


class TestPostQuery:
    """Test cases for PostQuery class."""

    def test_post_query_has_strawberry_definition(self):
        """Test if PostQuery is a valid Strawberry type."""
        assert hasattr(PostQuery, "__strawberry_definition__")

        field_names = [field.name for field in PostQuery.__strawberry_definition__.fields]
        assert "recent_posts" in field_names

    def test_recent_posts_valid_limit(self):
        """Test recent_posts with valid limit."""
        mock_posts = [Mock(), Mock()]

        with patch("apps.owasp.models.post.Post.recent_posts") as mock_recent:
            mock_recent.return_value.__getitem__ = Mock(return_value=mock_posts)

            query = PostQuery()
            query.recent_posts(limit=5)

            assert mock_recent.called

    def test_recent_posts_invalid_limit(self):
        """Test recent_posts with invalid limit returns empty list."""
        query = PostQuery()
        result = query.recent_posts(limit=0)
        assert result == []
        result = query.recent_posts(limit=-1)
        assert result == []
