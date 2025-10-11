"""A command to sync posts from owasp.org data."""

import json
import re

import yaml
import yaml.scanner
from django.core.management.base import BaseCommand

from apps.common.constants import OWASP_BLOG_URL, OWASP_URL
from apps.github.utils import get_repository_file_content
from apps.owasp.models.post import Post


class Command(BaseCommand):
    def get_author_image_url(self, author_image_url: str) -> str:
        """Return URL for author image.

        Args:
            author_image_url (str): The relative URL of the author's image.

        Returns:
            str: The full URL of the author's image.

        """
        return f"{OWASP_URL}{author_image_url}" if author_image_url else ""

    def get_blog_url(self, path: str) -> str:
        """Return OWASP blog URL for a given path.

        Args:
            path (str): The file path of the blog post.

        Returns:
            str: The full URL of the blog post.

        """
        pattern = re.compile(
            r"(https://raw\.githubusercontent\.com/OWASP/owasp\.github\.io/main/_posts/)"
            r"(\d{4})-(\d{2})-(\d{2})-"
            r"(.+)"
            r"\.md$"
        )
        match = pattern.match(path)

        return (
            f"{OWASP_BLOG_URL}/{match.group(2)}/{match.group(3)}/{match.group(4)}/"
            f"{match.group(5)}.html"
            if match
            else path
        )

    def handle(self, *args, **options) -> None:
        """Handle the command execution.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments.

        """
        # TODO(arkid15r): Add pagination support.
        post_repository_content = get_repository_file_content(
            "https://api.github.com/repos/OWASP/owasp.github.io/contents/_posts"
        )
        yaml_pattern = re.compile(r"^---\s*\n((?:(?!^---\s*$).*\n)+)^---\s*$", re.MULTILINE)

        posts = []
        for repository_file in json.loads(post_repository_content):
            if not repository_file.get("name", "").endswith(".md"):
                continue

            download_url = repository_file.get("download_url")
            post_content = get_repository_file_content(download_url)
            if not post_content.startswith("---"):
                continue

            try:
                if match := yaml_pattern.search(post_content):
                    metadata_yaml = match.group(1)
                    metadata = yaml.safe_load(metadata_yaml) or {}
            except yaml.scanner.ScannerError:
                metadata = {}

            data = {
                "author_image_url": self.get_author_image_url(metadata.get("author_image", "")),
                "author_name": metadata.get("author"),
                "published_at": metadata.get("date"),
                "title": metadata.get("title"),
                "url": self.get_blog_url(download_url),
            }

            if not all([data["title"], data["published_at"], data["author_name"], data["url"]]):
                self.stderr.write(
                    self.style.WARNING(
                        f"Skipping {repository_file.get('name')}: Missing required fields"
                    )
                )
                continue

            posts.append(Post.update_data(data, save=False))

        Post.bulk_save(posts)
