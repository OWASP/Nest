"""A command to update OWASP Nest index replicas."""

#!/usr/bin/env python3
from django.core.management.base import BaseCommand

from apps.owasp.index.project import ProjectIndex


class Command(BaseCommand):
    help = "Update OWASP Nest index replicas."

    def handle(self, *_args, **_options):
        print("\n Starting replica configuration...")
        ProjectIndex.configure_replicas()
        print("\n Replica have been Successfully created.")
