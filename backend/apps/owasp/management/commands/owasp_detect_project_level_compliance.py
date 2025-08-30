"""A command to detect and report project level compliance status."""

import logging

from django.core.management.base import BaseCommand

from apps.owasp.models.project import Project

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to detect and report project level compliance status.

    This is a reporting command only - it does not sync or update any data.
    For data synchronization, use the main data pipeline: make sync-data

    Architecture:
    - Part 1: Official level syncing happens during 'make update-data'
    - Part 2: Health scoring with compliance penalties happens during 'make sync-data'
    - This command: Reporting and analysis only
    """

    help = "Detect and report projects with non-compliant level assignments"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output showing all projects",
        )

    def handle(self, *args, **options):
        """Execute compliance detection and reporting."""
        verbose = options["verbose"]

        self.stdout.write("Analyzing project level compliance status...")

        # Get all active projects
        active_projects = Project.objects.filter(is_active=True).select_related()

        compliant_projects = []
        non_compliant_projects = []

        for project in active_projects:
            if project.is_level_compliant:
                compliant_projects.append(project)
                if verbose:
                    self.stdout.write(f"✓ {project.name}: {project.level} (matches official)")
            else:
                non_compliant_projects.append(project)
                self.stdout.write(
                    self.style.WARNING(
                        f"✗ {project.name}: Local={project.level}, "
                        f"Official={project.project_level_official}"
                    )
                )

        # Summary statistics
        total_projects = len(active_projects)
        compliant_count = len(compliant_projects)
        non_compliant_count = len(non_compliant_projects)
        compliance_rate = (compliant_count / total_projects * 100) if total_projects else 0.0

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("PROJECT LEVEL COMPLIANCE SUMMARY")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Total active projects: {total_projects}")
        self.stdout.write(f"Compliant projects: {compliant_count}")
        self.stdout.write(f"Non-compliant projects: {non_compliant_count}")
        self.stdout.write(f"Compliance rate: {compliance_rate:.1f}%")

        if non_compliant_count > 0:
            warning_msg = f"WARNING: Found {non_compliant_count} non-compliant projects"
            self.stdout.write(f"\n{self.style.WARNING(warning_msg)}")
            penalty_msg = (
                "These projects will receive score penalties in the next health score update."
            )
            self.stdout.write(penalty_msg)
        else:
            self.stdout.write(f"\n{self.style.SUCCESS('✓ All projects are level compliant!')}")

        # Log summary for monitoring
        logger.info(
            "Project level compliance analysis completed",
            extra={
                "total_projects": total_projects,
                "compliant_projects": compliant_count,
                "non_compliant_projects": non_compliant_count,
                "compliance_rate": f"{compliance_rate:.1f}%",
            },
        )

        # Check if official levels are populated
        from apps.owasp.models.enums.project import ProjectLevel

        default_level = ProjectLevel.OTHER
        projects_without_official_level = sum(
            1 for project in active_projects if project.project_level_official == default_level
        )

        if projects_without_official_level > 0:
            info_msg = (
                f"INFO: {projects_without_official_level} projects have default official levels"
            )
            self.stdout.write(f"\n{self.style.NOTICE(info_msg)}")
            sync_msg = (
                "Run 'make update-data' to sync official levels, "
                "then 'make sync-data' for scoring."
            )
            self.stdout.write(sync_msg)
