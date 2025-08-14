"""A command to detect and flag projects with non-compliant level assignments."""

import logging
import time

from django.core.management.base import BaseCommand, CommandError

from apps.owasp.utils.compliance_detector import ComplianceDetector
from apps.owasp.utils.project_level_fetcher import fetch_official_project_levels

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Detect and flag projects with non-compliant level assignments"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making actual updates'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output for debugging'
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='HTTP timeout for fetching project levels (default: 30 seconds)'
        )

    def handle(self, *args, **options):
        """Execute compliance detection workflow."""
        start_time = time.time()
        dry_run = options['dry_run']
        verbose = options['verbose']
        timeout = options['timeout']
        
        # Configure logging level based on verbose flag
        if verbose:
            logging.getLogger('apps.owasp.utils').setLevel(logging.DEBUG)
        
        try:
            self.stdout.write("Starting OWASP project level compliance detection...")
            
            if dry_run:
                self.stdout.write("DRY RUN MODE: No changes will be made to the database")
            
            # Step 1: Fetch official project levels
            self.stdout.write("Fetching official project levels from OWASP GitHub repository...")
            official_levels = fetch_official_project_levels(timeout=timeout)

            if official_levels is None or not official_levels:
                msg = "Failed to fetch official project levels or received empty payload"
                self.stderr.write(msg)
                raise CommandError(msg)

            self.stdout.write(
                f"Successfully fetched {len(official_levels)} official project levels"
            )
            
            # Step 2: Detect compliance issues
            self.stdout.write("Detecting compliance issues...")
            detector = ComplianceDetector()
            report = detector.detect_compliance_issues(official_levels)
            
            # Step 3: Log and display compliance findings
            self._log_compliance_findings(report)
            
from django.db import transaction

            # Step 4: Update compliance status (unless dry run)
            if not dry_run:
                self.stdout.write("Updating compliance status in database...")
                with transaction.atomic():
                    detector.update_compliance_status(report)
                self.stdout.write("Compliance status updated successfully")
            else:
                self.stdout.write("Skipping database updates due to dry-run mode")
            
            # Step 5: Summary
            execution_time = time.time() - start_time
            self.stdout.write(f"\nCompliance detection completed in {execution_time:.2f}s")
            self.stdout.write(f"Summary: {len(report.compliant_projects)} compliant, {len(report.non_compliant_projects)} non-compliant")
            self.stdout.write(f"Compliance rate: {report.compliance_rate:.1f}%")
            
            # Log detailed summary for monitoring
            logger.info(
                "Compliance detection completed successfully",
                extra={
                    "execution_time": f"{execution_time:.2f}s",
                    "dry_run": dry_run,
                    "total_projects": report.total_projects_checked,
                    "compliant_projects": len(report.compliant_projects),
                    "non_compliant_projects": len(report.non_compliant_projects),
                    "local_only_projects": len(report.local_only_projects),
                    "official_only_projects": len(report.official_only_projects),
                    "compliance_rate": f"{report.compliance_rate:.1f}%"
                }
            )
            
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            error_msg = f"Compliance detection failed after {execution_time:.2f}s: {e!s}"

            logger.exception(
                "Compliance detection failed",
                extra={
                    "execution_time_s": round(execution_time, 2),
                    "error": e.__class__.__name__,
                },
            )

            raise CommandError(error_msg) from e
    def _log_compliance_findings(self, report):
        """Log and display detailed compliance findings."""
        # Log level mismatches for non-compliant projects
        if report.non_compliant_projects:
            self.stderr.write(f"Found {len(report.non_compliant_projects)} non-compliant projects:")
            for project_name in report.non_compliant_projects:
                self.stderr.write(f"  - {project_name}")
                logger.warning(
                    "Level mismatch detected",
                    extra={"project": project_name}
                )
        
        # Log projects that exist locally but not in official data
        if report.local_only_projects:
            self.stdout.write(f"Found {len(report.local_only_projects)} projects that exist locally but not in official data:")
            for project_name in report.local_only_projects:
                self.stdout.write(f"  - {project_name}")
                logger.warning(
                    "Project exists locally but not in official data",
                    extra={"project": project_name}
                )
        
        # Log projects that exist in official data but not locally
        if report.official_only_projects:
            self.stdout.write(f"Found {len(report.official_only_projects)} projects in official data but not locally:")
            for project_name in report.official_only_projects:
                self.stdout.write(f"  - {project_name}")
                logger.info(
                    "Project exists in official data but not locally",
                    extra={"project": project_name}
                )
        
        # Log compliant projects
        if report.compliant_projects:
            self.stdout.write(f"Found {len(report.compliant_projects)} compliant projects")

