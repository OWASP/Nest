from unittest.mock import Mock, patch

import pytest
from datetime import datetime

from apps.owasp.models.post import Post


class TestPostModel:
    @pytest.mark.parametrize(
        ("title", "expected_str"),
        [
            ("Sample Post", "Sample Post"),
            ("", ""),
        ],
    )
    def test_post_str(self, title, expected_str):
        """Test the __str__ method of the Post model."""
        post = Post(
            title=title,
            url="https://example.com",
            published_at=datetime(2025, 1, 1)
        )
        assert str(post) == expected_str

    def test_bulk_save(self):
        """Test the bulk_save method."""
        mock_posts = [Mock(id=None), Mock(id=1)]
        with patch("apps.owasp.models.post.BulkSaveModel.bulk_save") as mock_bulk_save:
            Post.bulk_save(mock_posts, fields=["title"])
            mock_bulk_save.assert_called_once_with(Post, mock_posts, fields=["title"])

    @pytest.mark.parametrize(
        ("data", "expected_fields"),
        [
            (
                {"title": "New Post", "url": "https://example.com", "author_name": "John Doe", "published_at": datetime(2025, 1, 1), "author_image_url": "https://image.com"},
                {"title": "New Post", "url": "https://example.com", "author_name": "John Doe", "published_at": datetime(2025, 1, 1), "author_image_url": "https://image.com"},
            ),
            (
                {"author_image_url": "https://image.com", "url": "https://example.com"},
                {"author_image_url": "https://image.com", "url": "https://example.com"},
            ),
        ],
    )
    def test_from_dict_updates_fields(self, data, expected_fields):
        """Test the from_dict method updates fields correctly."""
        post = Post()
        post.from_dict(data)
        for field, value in expected_fields.items():
            assert getattr(post, field) == value

    @patch("apps.owasp.models.post.Post.objects.get")
    def test_update_data_existing_post(self, mock_get):
        """Test update_data updates existing post."""
        mock_post = Mock()
        mock_get.return_value = mock_post
        data = {"url": "https://existing.com", "title": "Updated Title", "author_name": "Updated Author", "author_image_url": "https://updatedimage.com"}
        
        result = Post.update_data(data)
        
        mock_get.assert_called_once_with(url=data["url"])
        mock_post.from_dict.assert_called_once_with(data)
        mock_post.save.assert_called_once()
        assert result == mock_post

    def test_update_data_missing_url(self):
        """Test update_data returns None when url is missing."""
        assert Post.update_data({"title": "No URL"}) is None

    @patch("apps.owasp.models.post.Post.objects.all")
    def test_recent_posts_ordering(self, mock_all):
        """Test recent_posts uses correct ordering."""
        mock_queryset = Mock()
        mock_all.return_value = mock_queryset
        
        result = Post.recent_posts()
        
        mock_queryset.order_by.assert_called_once_with("-published_at")
        assert result == mock_queryset.order_by.return_value
