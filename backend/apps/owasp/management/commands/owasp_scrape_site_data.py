"""A command to update OWASP entities from owasp.org data."""

import time

import requests
from django.core.management.base import BaseCommand
from lxml import etree, html

from apps.github.utils import normalize_url
from apps.owasp.models import Project


class Command(BaseCommand):
    help = "Updates OWASP entities based on their owasp.org data."

    def handle(self, *args, **_options):
        projects = Project.objects.filter(
            is_active=True,
            owasp_repository__is_archived=False,
            owasp_repository__is_empty=False,
        ).order_by("owasp_repository__created_at")

        updated_projects = []
        for idx, project in enumerate(projects):
            print(f"{idx + 1:<3}", project.owasp_url)

            page_response = requests.get(project.owasp_url, timeout=10)
            if page_response.status_code == requests.codes.not_found:
                project.deactivate()
                continue

            try:
                page_tree = html.fromstring(page_response.content)
            except etree.ParserError:
                project.deactivate()
                continue

            # Get GitHub URLs.
            scraped_urls = sorted(
                {
                    normalize_url(url)
                    for url in set(
                        page_tree.xpath(
                            "//div[@class='sidebar']//a[contains(@href, 'github.com')]/@href"
                        )
                    )
                    if project.check_owasp_entity_repository(url)
                }
            )
            # Check for redirects.
            repositories_urls = set()
            for scraped_url in scraped_urls:
                github_response = requests.get(scraped_url, allow_redirects=False, timeout=10)
                if github_response.status_code == requests.codes.ok:
                    repositories_urls.add(scraped_url)
                elif github_response.status_code in {
                    requests.codes.moved_permanently,  # 301
                    requests.codes.found,  # 302
                    requests.codes.see_other,  # 303
                    requests.codes.temporary_redirect,  # 307
                    requests.codes.permanent_redirect,  # 308
                }:
                    repositories_urls.add(normalize_url(github_response.headers["Location"]))

            if repositories_urls:
                project.repositories_raw = sorted(repositories_urls)

            # Get leaders.
            leaders_header = page_tree.xpath('//*[@id="leaders"]')
            if leaders_header:
                leaders_ul = leaders_header[0].getnext()
                if leaders_ul is not None and leaders_ul.tag == "ul":
                    leaders = sorted(name.strip() for name in leaders_ul.xpath(".//li/a/text()"))
                    if leaders:
                        project.leaders_raw = leaders

            if leaders or repositories_urls:
                updated_projects.append(project)

            time.sleep(0.5)

        Project.objects.bulk_update(
            updated_projects,
            fields=[field.name for field in Project._meta.fields if not field.primary_key],  # noqa: SLF001
        )
