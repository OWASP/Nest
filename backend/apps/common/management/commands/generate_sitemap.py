"""Management command to generate XML sitemaps for the website."""

from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.github.models.user import User
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.project import Project


class Command(BaseCommand):
    help = "Generate XML sitemaps for the website"

    def __init__(self):
        """Initialize the command with site URL and static routes."""
        super().__init__()
        self.site_url = settings.SITE_URL
        self.static_routes = {
            "projects": [
                {"path": "/projects", "changefreq": "weekly", "priority": 0.9},
                {"path": "/projects/contribute", "changefreq": "daily", "priority": 0.6},
            ],
            "chapters": [
                {"path": "/chapters", "changefreq": "weekly", "priority": 0.8},
            ],
            "committees": [
                {"path": "/committees", "changefreq": "monthly", "priority": 0.8},
            ],
            "users": [
                {"path": "/community/users", "changefreq": "daily", "priority": 0.7},
            ],
        }

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            default=settings.STATIC_ROOT,
            help="Directory where sitemap files will be saved",
        )

    def handle(self, *args, **options):
        output_dir = Path(options["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        sitemap_files = [
            "sitemap-project.xml",
            "sitemap-chapter.xml",
            "sitemap-committee.xml",
            "sitemap-user.xml",
        ]

        self.generate_project_sitemap(output_dir)
        self.generate_chapter_sitemap(output_dir)
        self.generate_committee_sitemap(output_dir)
        self.generate_user_sitemap(output_dir)

        index_content = self.generate_index_sitemap(sitemap_files)
        index_path = output_dir / "sitemap.xml"
        self.save_sitemap(index_content, index_path)

        self.stdout.write(self.style.SUCCESS(f"Successfully generated sitemaps in {output_dir}"))

    def generate_project_sitemap(self, output_dir):
        """Generate sitemap for projects."""
        routes = self.static_routes["projects"]
        projects = Project.objects.all()
        indexable_projects = [project for project in projects if project.is_indexable]

        routes.extend(
            [
                {"path": f"/projects/{project.nest_key}", "changefreq": "weekly", "priority": 0.7}
                for project in indexable_projects
            ]
        )

        content = self.generate_sitemap_content(routes)
        self.save_sitemap(content, output_dir / "sitemap-project.xml")

    def generate_chapter_sitemap(self, output_dir):
        """Generate sitemap for chapters."""
        routes = self.static_routes["chapters"]
        chapters = Chapter.objects.filter(is_active=True)
        indexable_chapters = [chapter for chapter in chapters if chapter.is_indexable]

        routes.extend(
            [
                {"path": f"/chapters/{chapter.nest_key}", "changefreq": "weekly", "priority": 0.7}
                for chapter in indexable_chapters
            ]
        )

        content = self.generate_sitemap_content(routes)
        self.save_sitemap(content, output_dir / "sitemap-chapter.xml")

    def generate_committee_sitemap(self, output_dir):
        """Generate sitemap for committees."""
        routes = self.static_routes["committees"]
        indexable_committees = Committee.objects.filter(is_active=True)

        routes.extend(
            [
                {
                    "path": f"/committees/{committee.nest_key}",
                    "changefreq": "weekly",
                    "priority": 0.7,
                }
                for committee in indexable_committees
            ]
        )

        content = self.generate_sitemap_content(routes)
        self.save_sitemap(content, output_dir / "sitemap-committee.xml")

    def generate_user_sitemap(self, output_dir):
        """Generate sitemap for users."""
        routes = self.static_routes["users"]
        users = User.objects.all()
        indexable_users = [user for user in users if user.is_indexable]

        routes.extend(
            [
                {"path": f"/community/users/{user.login}", "changefreq": "weekly", "priority": 0.7}
                for user in indexable_users
            ]
        )

        content = self.generate_sitemap_content(routes)
        self.save_sitemap(content, output_dir / "sitemap-user.xml")

    def generate_sitemap_content(self, routes):
        """Generate sitemap content for a set of routes."""
        urls = []
        lastmod = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        for route in routes:
            url_entry = {
                "loc": f"{self.site_url}{route['path']}",
                "lastmod": lastmod,
                "changefreq": route["changefreq"],
                "priority": str(route["priority"]),
            }
            urls.append(self.create_url_entry(url_entry))

        return self.create_sitemap(urls)

    def generate_index_sitemap(self, sitemap_files):
        """Generate the sitemap index file."""
        sitemaps = []
        lastmod = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        for sitemap_file in sitemap_files:
            sitemap_entry = {"loc": f"{self.site_url}/{sitemap_file}", "lastmod": lastmod}
            sitemaps.append(self.create_sitemap_index_entry(sitemap_entry))

        return self.create_sitemap_index(sitemaps)

    def create_url_entry(self, url_data):
        """Create a URL entry for the sitemap."""
        url_template = (
            "  <url>\n"
            "    <loc>{loc}</loc>\n"
            "    <lastmod>{lastmod}</lastmod>\n"
            "    <changefreq>{changefreq}</changefreq>\n"
            "    <priority>{priority}</priority>\n"
            "  </url>"
        )
        return url_template.format(**url_data)

    def create_sitemap_index_entry(self, sitemap_data):
        """Create a sitemap entry for the index."""
        sitemap_template = (
            "  <sitemap>\n"
            "    <loc>{loc}</loc>\n"
            "    <lastmod>{lastmod}</lastmod>\n"
            "  </sitemap>"
        )
        return sitemap_template.format(**sitemap_data)

    def create_sitemap(self, urls):
        """Create the complete sitemap XML."""
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{chr(10).join(urls)}\n"
            "</urlset>"
        )

    def create_sitemap_index(self, sitemaps):
        """Create the complete sitemap index XML."""
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{chr(10).join(sitemaps)}\n"
            "</sitemapindex>"
        )

    @staticmethod
    def save_sitemap(content, filepath):
        """Save the sitemap content to a file."""
        with filepath.open("w", encoding="utf-8") as f:
            f.write(content)
