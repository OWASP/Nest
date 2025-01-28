"""A command to add OWASP sponsors data."""

import yaml
from django.core.management.base import BaseCommand

from apps.github.utils import get_repository_file_content, normalize_url
from apps.owasp.models.sponsor import Sponsor


class Command(BaseCommand):
    help = "Import sponsors from OWASP GitHub repository"

    def handle(self, *args, **kwargs):
        url = "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/corp_members.yml"
        yaml_content = get_repository_file_content(url).replace("\t", "    ")
        data = yaml.safe_load(yaml_content)

        for entry in data:
            fields = {
                "name": entry.get("name", ""),
                "sort_name": entry.get("sortname", "").capitalize(),
                "description": entry.get("description", ""),
                "url": normalize_url(entry.get("url", "")) or "",
                "job_url": normalize_url(entry.get("job_url", "")) or "",
                "image_path": entry.get("image", ""),
                "is_member": entry.get("member", False),
                "member_type": entry.get("membertype", "4") or "4",
                "sponsor_type": entry.get("sponsor", "-1") or "-1",
            }

            sponsor = Sponsor(**fields)
            sponsor.save()
            self.stdout.write(self.style.SUCCESS(f"Successfully imported sponsor: {sponsor.name}"))

        self.stdout.write(self.style.SUCCESS("Finished importing sponsors"))
