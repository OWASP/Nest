"""A command to update OWASP posts from owasp.org data."""

import json
import re

import yaml
import yaml.scanner
from django.core.management.base import BaseCommand

from apps.github.utils import get_repository_file_content
from apps.owasp.models.post import Post


class Command(BaseCommand):
    def handle(self, *args, **options):
        post_repository_content = get_repository_file_content(
            "https://api.github.com/repos/OWASP/owasp.github.io/contents/_posts"
        )
        repository_files = json.loads(post_repository_content)
        posts = []

        for repository_file in repository_files:
            if repository_file.get("name", "").endswith(".md"):
                download_url = repository_file.get("download_url")
                post_content = get_repository_file_content(download_url)

                if post_content.startswith("---"):
                    try:
                        yaml_content = re.search(r"^---\s*(.*?)\s*---", post_content, re.DOTALL)
                        metadata = (
                            yaml.safe_load(yaml_content.group(1)) or {} if yaml_content else {}
                        )
                    except yaml.scanner.ScannerError:
                        metadata = {}

                    data = {
                        "title": metadata.get("title"),
                        "published_at": metadata.get("date"),
                        "author_name": metadata.get("author"),
                        "author_image_url": metadata.get("author_image", ""),
                        "url": download_url.replace(
                            "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_posts/",
                            "https://owasp.org/blog/",
                        ),
                    }

                    post = Post.update_data(data, save=False)
                    if post:
                        posts.append(post)

        Post.bulk_save(
            posts, fields=["title", "published_at", "author_name", "author_image_url", "url"]
        )
