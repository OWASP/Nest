"""A command to detect and flag projects with non-compliant level assignments."""

import logging
import time

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.owasp.utils.compliance_detector import detect_and_update_compliance
from apps.owasp.utils.project_level_fetcher import fetch_official_project_levels
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics

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
        start_time = time.perf_counter()
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
            
            # Steps 2-4: Detect and update in one procedural call
            self.stdout.write("Detecting and updating compliance issues...")
            detect_and_update_compliance(official_levels)
            
            # Recompute a lightweight summary from latest health metrics
            latest_metrics = ProjectHealthMetrics.get_latest_health_metrics()
            total = len(latest_metrics)
            compliant = sum(1 for m in latest_metrics if m.is_level_compliant)
            non_compliant = total - compliant
            compliance_rate = (compliant / total * 100) if total else 0.0

            
            # Step 5: Summary
            execution_time = time.perf_counter() - start_time
            self.stdout.write(f"\nCompliance detection completed in {execution_time:.2f}s")
            self.stdout.write(f"Summary: {compliant} compliant, {non_compliant} non-compliant")
            self.stdout.write(f"Compliance rate: {compliance_rate:.1f}%")
            
            # Log detailed summary for monitoring
            logger.info(
                "Compliance detection completed successfully",
                extra={
                    "execution_time": f"{execution_time:.2f}s",
                    "dry_run": dry_run,
                    "total_projects": total,
                    "compliant_projects": compliant,
                    "non_compliant_projects": non_compliant,
                    "compliance_rate": f"{compliance_rate:.1f}%"
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
  