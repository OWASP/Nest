"""A command to generate OWASP community snapshot video."""

import logging
import os
import tempfile
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.owasp.models.snapshot import Snapshot
from apps.owasp.video import SlideBuilder, VideoGenerator

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generate OWASP community snapshot video."

    def add_arguments(self, parser) -> None:
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument(
            "--output-dir",
            default=Path(tempfile.gettempdir()),
            type=Path,
            help="Directory to save the generated video.",
        )
        parser.add_argument(
            "--snapshot-key",
            required=True,
            type=str,
            help="Snapshot key (e.g., '2025-06' for month or '2025' for year).",
        )

    def handle(self, *args, **options) -> None:
        """Handle the command execution."""
        # Required to cache fonts
        os.environ["XDG_CACHE_HOME"] = str(Path(tempfile.gettempdir()) / "cache")

        snapshot_key = options["snapshot_key"]
        output_dir = options["output_dir"]
        output_dir.mkdir(parents=True, exist_ok=True)

        snapshots = Snapshot.objects.filter(
            key__startswith=snapshot_key, status=Snapshot.Status.COMPLETED
        ).order_by("start_at")

        if not snapshots:
            logger.error("No completed snapshots found for key: %s", snapshot_key)
            return

        self.stdout.write(f"Generating a video for snapshot: {snapshot_key}")

        slide_builder = SlideBuilder(snapshots)
        generator = VideoGenerator()

        slides_to_add = [
            slide_builder.create_intro_slide(),
            slide_builder.create_sponsors_slide(),
            slide_builder.create_projects_slide(),
            slide_builder.create_chapters_slide(),
            slide_builder.create_releases_slide(),
            slide_builder.create_thank_you_slide(),
        ]

        for slide in slides_to_add:
            if slide is not None:
                generator.append_slide(slide)

        video_path = output_dir / f"{snapshot_key}_snapshot.mp4"
        generator.generate_video(video_path)
        self.stdout.write(f"Generated a video at {video_path}")
