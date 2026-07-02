"""A command to generate OWASP community snapshot video."""

import logging
import tempfile
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.owasp.models.snapshot import Snapshot
from apps.owasp.video import SlideBuilder, VideoGenerator

logger = logging.getLogger(__name__)

VIDEO_DIR_PREFIX = "community_snapshot_video"


class Command(BaseCommand):
    help = "Generate OWASP community snapshot video."

    def add_arguments(self, parser) -> None:
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument(
            "snapshot_key",
            type=str,
            help="Snapshot key (e.g., '2025-06' for month or '2025' for year).",
        )
        parser.add_argument(
            "output_dir",
            type=str,
            help="Directory to save the video to.",
        )

    def handle(self, *args, **options) -> None:
        """Handle the command execution."""
        snapshot_key = options["snapshot_key"]
        output_dir = options["output_dir"]

        snapshots = Snapshot.objects.filter(
            key__startswith=snapshot_key, status=Snapshot.Status.COMPLETED
        ).order_by("start_at")

        if not snapshots:
            logger.error("No completed snapshots found for key: %s", snapshot_key)
            return

        self.stdout.write(f"Generating a video for snapshot: {snapshot_key}")

        dir_name = f"{VIDEO_DIR_PREFIX}_{snapshot_key}"
        video_output_dir = Path(output_dir) / dir_name
        temp_output_dir = Path(tempfile.gettempdir()) / dir_name
        video_output_dir.mkdir(parents=True, exist_ok=True)
        temp_output_dir.mkdir(parents=True, exist_ok=True)

        slide_builder = SlideBuilder(snapshots, output_dir=temp_output_dir)
        generator = VideoGenerator()

        slides_to_add = [
            slide_builder.add_intro_slide(),
            slide_builder.add_sponsors_slide(),
            slide_builder.add_projects_slide(),
            slide_builder.add_chapters_slide(),
            slide_builder.add_releases_slide(),
            slide_builder.add_thank_you_slide(),
        ]

        for slide in slides_to_add:
            if slide is not None:
                generator.append_slide(slide)

        video_path = generator.generate_video(video_output_dir, f"{snapshot_key}_snapshot")
        generator.cleanup()

        self.stdout.write(
            self.style.SUCCESS(
                f"Generated video at backend/generated_videos/{dir_name}/{video_path.name}"
            )
        )
