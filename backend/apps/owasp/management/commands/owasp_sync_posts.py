import requests
import yaml
from django.core.management.base import BaseCommand
from apps.github.utils import get_repository_file_content
from apps.owasp.models.post import Post

class Command(BaseCommand):

    def handle(self, *args, **options):
        posts_api_url = "https://api.github.com/repos/OWASP/owasp.github.io/contents/_posts"
        response = requests.get(posts_api_url)
        files = response.json()
        posts = []

        for file in files:
            if file.get('name', '').endswith('.md'):
                download_url = file.get('download_url')
                file_content = get_repository_file_content(download_url)

                if file_content.startswith('---'):
                    parts = file_content.split('---')
                    metadata = yaml.safe_load(parts[1])

                    title = metadata.get('title')
                    date = metadata.get('date')
                    author = metadata.get('author')
                    author_image = metadata.get('author_image', '')
                    url = download_url.replace('https://raw.githubusercontent.com/OWASP/owasp.github.io/main', 'https://github.com/OWASP/owasp.github.io/tree/main')

                    post = Post(
                        title=title,
                        date=date,
                        author=author,
                        author_image=author_image,
                        url=url
                    )
                    posts.append(post)
        
        Post.bulk_save(posts, fields=["title", "date", "author", "author_image", "url"])