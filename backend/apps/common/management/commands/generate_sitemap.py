"""Management command to generate OWASP Nest sitemap."""

from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.common.constants import NL
from apps.github.models.user import User
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.project import Project


class Command(BaseCommand):
    help = "Generate sitemap"

    static_routes = {
        "chapters": [{"path": "/chapters", "changefreq": "weekly", "priority": 0.8}],
        "committees": [{"path": "/committees", "changefreq": "monthly", "priority": 0.8}],
        "projects": [
            {"path": "/projects", "changefreq": "weekly", "priority": 0.9},
            {"path": "/projects/contribute", "changefreq": "daily", "priority": 0.6},
        ],
        "users": [
            {"path": "/community/users", "changefreq": "daily", "priority": 0.7},
        ],
    }

    def add_arguments(self, parser):
        """Add command-line arguments to the parser.

        Args:
            parser (ArgumentParser): The argument parser instance.
        """
        parser.add_argument(
            "--output-dir",
            default=settings.STATIC_ROOT,
            help="Directory where sitemap files will be saved",
        )

    def handle(self, *args, **options):
        """Generate sitemaps for the OWASP Nest application.

        Args:
            *args: Positional arguments (not used).
            **options: Command-line options.
        """
        output_dir = Path(options["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        sitemap_files = [
            "sitemap-chapters.xml",
            "sitemap-committees.xml",
            "sitemap-projects.xml",
            "sitemap-users.xml",
        ]

        self.generate_chapter_sitemap(output_dir)
        self.generate_committee_sitemap(output_dir)
        self.generate_project_sitemap(output_dir)
        self.generate_user_sitemap(output_dir)

        index_content = self.generate_index_sitemap(sitemap_files)
        index_path = output_dir / "sitemap.xml"
        self.save_sitemap(index_content, index_path)

        self.stdout.write(self.style.SUCCESS(f"Successfully generated sitemaps in {output_dir}"))

    def generate_project_sitemap(self, output_dir):
        """Generate a sitemap for projects.

        Args:
            output_dir (Path): The directory to save the sitemap.
        """
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
        """Generate a sitemap for chapters.

        Args:
            output_dir (Path): The directory to save the sitemap.
        """
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
        self.save_sitemap(content, output_dir / "sitemap-chapters.xml")

    def generate_committee_sitemap(self, output_dir):
        """Generate a sitemap for committees.

        Args:
            output_dir (Path): The directory to save the sitemap.
        """
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
        self.save_sitemap(content, output_dir / "sitemap-committees.xml")

    def generate_user_sitemap(self, output_dir):
        """Generate a sitemap for users.

        Args:
            output_dir (Path): The directory to save the sitemap.
        """
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
        self.save_sitemap(content, output_dir / "sitemap-users.xml")

    def generate_sitemap_content(self, routes):
        """Generate the XML content for a sitemap.

        Args:
            routes (list): A list of route dictionaries.

        Returns:
            str: The XML content of the sitemap.
        """
        urls = []
        lastmod = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        for route in routes:
            url_entry = {
                "loc": f"{settings.SITE_URL}{route['path']}",
                "lastmod": lastmod,
                "changefreq": route["changefreq"],
                "priority": str(route["priority"]),
            }
            urls.append(self.create_url_entry(url_entry))

        return self.create_sitemap(urls)

    def generate_index_sitemap(self, sitemap_files):
        """Generate the sitemap index file.

        Args:
            sitemap_files (list): A list of sitemap file names.

        Returns:
            str: The XML content of the sitemap index.
        """
        sitemaps = []
        lastmod = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        for sitemap_file in sitemap_files:
            sitemap_entry = {"loc": f"{settings.SITE_URL}/{sitemap_file}", "lastmod": lastmod}
            sitemaps.append(self.create_sitemap_index_entry(sitemap_entry))

        return self.create_sitemap_index(sitemaps)

    def create_url_entry(self, url_data):
        """Create a URL entry for the sitemap.

        Args:
            url_data (dict): A dictionary containing URL data.

        Returns:
            str: The XML entry for the URL.
        """
        return (
            "  <url>\n"
            "    <loc>{loc}</loc>\n"
            "    <lastmod>{lastmod}</lastmod>\n"
            "    <changefreq>{changefreq}</changefreq>\n"
            "    <priority>{priority}</priority>\n"
            "  </url>"
        ).format(**url_data)

    def create_sitemap_index_entry(self, sitemap_data):
        """Create a sitemap index entry.

        Args:
            sitemap_data (dict): A dictionary containing sitemap data.

        Returns:
            str: The XML entry for the sitemap index.
        """
        return (
            "  <sitemap>\n"
            "    <loc>{loc}</loc>\n"
            "    <lastmod>{lastmod}</lastmod>\n"
            "  </sitemap>"
        ).format(**sitemap_data)

    def create_sitemap(self, urls):
        """Create the complete sitemap XML.

        Args:
            urls (list): A list of URL entries.

        Returns:
            str: The XML content of the sitemap.
        """
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{NL.join(urls)}\n"
            "</urlset>"
        )

    def create_sitemap_index(self, sitemaps):
        """Create the complete sitemap index XML.

        Args:
            sitemaps (list): A list of sitemap index entries.

        Returns:
            str: The XML content of the sitemap index.
        """
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{NL.join(sitemaps)}\n"
            "</sitemapindex>"
        )

    @staticmethod
    def save_sitemap(content, filepath):
        """Save the sitemap content to a file.

        Args:
            content (str): The XML content of the sitemap.
            filepath (Path): The file path to save the sitemap.
        """
        with filepath.open("w", encoding="utf-8") as f:
            f.write(content)
