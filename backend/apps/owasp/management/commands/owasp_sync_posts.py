"""A command to sync posts from owasp.org data."""

import json
import re

import yaml
import yaml.scanner
from django.core.management.base import BaseCommand

from apps.common.utils import get_author_image_url, get_blog_url
from apps.github.utils import get_repository_file_content
from apps.owasp.models.post import Post


class Command(BaseCommand):
    def handle(self, *args, **options):
        post_repository_content = get_repository_file_content(
            "https://api.github.com/repos/OWASP/owasp.github.io/contents/_posts"
        )
        repository_files = json.loads(post_repository_content)
        posts = []

        yaml_pattern = re.compile(r"^---\s*\n((?:(?!^---\s*$).*\n)+)^---\s*$", re.MULTILINE)

        for repository_file in repository_files:
            if repository_file.get("name", "").endswith(".md"):
                download_url = repository_file.get("download_url")
                post_content = get_repository_file_content(download_url)

                if post_content.startswith("---"):
                    try:
                        match = yaml_pattern.search(post_content)
                        if match:
                            metadata_yaml = match.group(1)
                            metadata = yaml.safe_load(metadata_yaml) or {}
                        else:
                            metadata = {}
                    except yaml.scanner.ScannerError:
                        metadata = {}

                    data = {
                        "title": metadata.get("title"),
                        "published_at": metadata.get("date"),
                        "author_name": metadata.get("author"),
                        "author_image_url": get_author_image_url(metadata.get("author_image", "")),
                        "url": get_blog_url(download_url),
                    }

                    if not all([data["title"], data["published_at"], data["author_name"]]):
                        self.stderr.write(
                            self.style.WARNING(
                                f"Skipping {repository_file.get('name')}: Missing required fields"
                            )
                        )
                        continue

                    post = Post.update_data(data, save=False)
                    if post:
                        posts.append(post)

        Post.bulk_save(
            posts, fields=["title", "published_at", "author_name", "author_image_url", "url"]
        )
