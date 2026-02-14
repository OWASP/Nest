import json
from datetime import date
from unittest import mock

import pytest

from apps.owasp.management.commands.owasp_sync_posts import Command


class TestUpdateOwaspPostsCommand:
    TOTAL_API_CALLS = 3
    TOTAL_UPDATE_CALLS = 2

    @pytest.fixture
    def command(self):
        cmd = Command()
        cmd.stdout = mock.Mock()
        cmd.stderr = mock.Mock()
        cmd.style = mock.Mock()
        return cmd

    @pytest.fixture
    def mock_repository_files(self):
        return [
            {
                "name": "2023-01-01-test-post.md",
                "download_url": "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_posts/2023-01-01-test-post.md",
            },
            {
                "name": "2023-01-02-another-post.md",
                "download_url": "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_posts/2023-01-02-another-post.md",
            },
        ]

    @pytest.fixture
    def mock_post_content(self):
        return """---
title: Test Post
date: 2023-01-01
author: John Doe
author_image: /assets/images/people/john.jpg
---

This is the content of the test post."""

    @mock.patch("apps.owasp.management.commands.owasp_sync_posts.get_repository_file_content")
    @mock.patch("apps.owasp.models.post.Post.update_data")
    @mock.patch("apps.owasp.models.post.Post.bulk_save")
    def test_handle_successful_processing(
        self,
        mock_bulk_save,
        mock_update_data,
        mock_get_content,
        command,
        mock_repository_files,
        mock_post_content,
    ):
        mock_get_content.side_effect = [
            json.dumps(mock_repository_files),
            mock_post_content,
            mock_post_content,
        ]

        mock_post1 = mock.Mock()
        mock_post2 = mock.Mock()
        mock_update_data.side_effect = [mock_post1, mock_post2]

        command.handle()

        assert mock_get_content.call_count == self.TOTAL_API_CALLS
        mock_get_content.assert_any_call(
            "https://api.github.com/repos/OWASP/owasp.github.io/contents/_posts"
        )
        mock_get_content.assert_any_call(mock_repository_files[0]["download_url"])
        mock_get_content.assert_any_call(mock_repository_files[1]["download_url"])

        assert mock_update_data.call_count == self.TOTAL_UPDATE_CALLS

        mock_update_data.assert_any_call(
            {
                "title": "Test Post",
                "published_at": date(2023, 1, 1),
                "author_name": "John Doe",
                "author_image_url": "https://owasp.org/assets/images/people/john.jpg",
                "url": "https://owasp.org/blog/2023/01/01/test-post.html",
            },
            save=False,
        )

        mock_update_data.assert_any_call(
            {
                "title": "Test Post",
                "published_at": date(2023, 1, 1),
                "author_name": "John Doe",
                "author_image_url": "https://owasp.org/assets/images/people/john.jpg",
                "url": "https://owasp.org/blog/2023/01/02/another-post.html",
            },
            save=False,
        )

        mock_bulk_save.assert_called_once_with([mock_post1, mock_post2])

    @mock.patch("apps.owasp.management.commands.owasp_sync_posts.get_repository_file_content")
    @mock.patch("apps.owasp.models.post.Post.update_data")
    @mock.patch("apps.owasp.models.post.Post.bulk_save")
    def test_handle_with_no_front_matter(
        self, mock_bulk_save, mock_update_data, mock_get_content, command, mock_repository_files
    ):
        no_front_matter = "This is a post without front matter"

        mock_get_content.side_effect = [
            json.dumps(mock_repository_files),
            no_front_matter,
            no_front_matter,
        ]

        command.handle()

        assert mock_get_content.call_count == self.TOTAL_API_CALLS
        assert mock_update_data.call_count == 0
        mock_bulk_save.assert_called_once_with([])

    @mock.patch("apps.owasp.management.commands.owasp_sync_posts.get_repository_file_content")
    @mock.patch("apps.owasp.models.post.Post.update_data")
    @mock.patch("apps.owasp.models.post.Post.bulk_save")
    def test_handle_when_update_data_returns_none(
        self,
        mock_bulk_save,
        mock_update_data,
        mock_get_content,
        command,
        mock_repository_files,
        mock_post_content,
    ):
        mock_get_content.side_effect = [
            json.dumps(mock_repository_files),
            mock_post_content,
            mock_post_content,
        ]

        mock_update_data.return_value = None

        command.handle()

        assert mock_get_content.call_count == self.TOTAL_API_CALLS
        assert mock_update_data.call_count == self.TOTAL_UPDATE_CALLS
        mock_bulk_save.assert_called_once_with([None, None])

    @mock.patch("apps.owasp.management.commands.owasp_sync_posts.get_repository_file_content")
    @mock.patch("apps.owasp.models.post.Post.update_data")
    @mock.patch("apps.owasp.models.post.Post.bulk_save")
    def test_handle_skip_non_md_files(
        self, mock_bulk_save, mock_update_data, mock_get_content, command
    ):
        """Test handle skips non-.md files."""
        repository_files = [
            {"name": "readme.txt", "download_url": "https://example.com/readme.txt"},
            {"name": "image.png", "download_url": "https://example.com/image.png"},
        ]

        mock_get_content.side_effect = [json.dumps(repository_files)]

        command.handle()

        assert mock_get_content.call_count == 1
        mock_update_data.assert_not_called()
        mock_bulk_save.assert_called_once_with([])

    @mock.patch("apps.owasp.management.commands.owasp_sync_posts.get_repository_file_content")
    @mock.patch("apps.owasp.models.post.Post.update_data")
    @mock.patch("apps.owasp.models.post.Post.bulk_save")
    def test_handle_yaml_scanner_error(
        self, mock_bulk_save, mock_update_data, mock_get_content, command
    ):
        """Test handle when YAML content triggers ScannerError."""
        repository_files = [
            {
                "name": "2023-01-01-bad-yaml.md",
                "download_url": "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_posts/2023-01-01-bad-yaml.md",
            },
        ]

        bad_yaml_content = "---\nbad: yaml: {[: invalid\n---\n"

        mock_get_content.side_effect = [json.dumps(repository_files), bad_yaml_content]

        command.handle()

        assert mock_get_content.call_count == 2
        mock_update_data.assert_not_called()
        mock_bulk_save.assert_called_once_with([])

    @mock.patch("apps.owasp.management.commands.owasp_sync_posts.get_repository_file_content")
    @mock.patch("apps.owasp.models.post.Post.update_data")
    @mock.patch("apps.owasp.models.post.Post.bulk_save")
    def test_handle_missing_required_fields(
        self, mock_bulk_save, mock_update_data, mock_get_content, command
    ):
        """Test handle when post has valid frontmatter but missing required fields."""
        repository_files = [
            {
                "name": "2023-01-01-incomplete.md",
                "download_url": "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_posts/2023-01-01-incomplete.md",
            },
        ]

        incomplete_content = "---\nauthor_image: /assets/images/people/test.jpg\n---\nContent"

        mock_get_content.side_effect = [json.dumps(repository_files), incomplete_content]

        command.handle()

        assert mock_get_content.call_count == 2
        mock_update_data.assert_not_called()
        mock_bulk_save.assert_called_once_with([])
        command.stderr.write.assert_called()
