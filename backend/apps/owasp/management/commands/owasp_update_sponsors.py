"""A command to add OWASP sponsors data."""

import yaml
from django.core.management.base import BaseCommand

from apps.github.utils import get_repository_file_content
from apps.owasp.models.sponsor import Sponsor


class Command(BaseCommand):
    help = "Import sponsors from the provided YAML file"

    def handle(self, *args, **kwargs):
        """Handle the command execution.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        sponsors = yaml.safe_load(
            get_repository_file_content(
                "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/corp_members.yml"
            ).expandtabs()
        )

        Sponsor.bulk_save([Sponsor.update_data(sponsor) for sponsor in sponsors])
