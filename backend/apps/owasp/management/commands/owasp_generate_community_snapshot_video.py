"""A command to generate OWASP community snapshot video."""

import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import ffmpeg
import pypdfium2 as pdfium
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from weasyprint import HTML

from apps.common.eleven_labs import ElevenLabs
from apps.owasp.models.snapshot import Snapshot
from apps.owasp.models.sponsor import Sponsor

logger = logging.getLogger(__name__)

AUDIO_EXTENSION = ".mp3"
ELEVENLABS_STABILITY = 0.4
ELEVENLABS_STYLE = 0.1
IMAGE_EXTENSION = ".png"
IMAGE_FORMAT = "PNG"
MAX_DETAILED_PROJECTS = 20
MAX_TRANSCRIPT_PROJECTS = 4
OUTPUT_DIR = Path(tempfile.gettempdir())
PDF_RENDER_SCALE = 2
VIDEO_EXTENSION = ".mp4"
VIDEO_FRAMERATE = 60


@dataclass
class Slide:
    """Represents a single video slide."""

    context: dict[str, Any]
    name: str
    output_dir: Path
    template_name: str
    transcript: str | None = None

    @property
    def audio_path(self) -> Path:
        return self.output_dir / f"{self.name}{AUDIO_EXTENSION}"

    @property
    def image_path(self) -> Path:
        return self.output_dir / f"{self.name}{IMAGE_EXTENSION}"

    @property
    def video_path(self) -> Path:
        return self.output_dir / f"{self.name}{VIDEO_EXTENSION}"

    def render_and_save_image(self) -> None:
        """Render an HTML template as an image."""
        page = None
        pdf = None
        try:
            html_content = render_to_string(self.template_name, self.context)

            html = HTML(string=html_content)

            pdf = pdfium.PdfDocument(html.write_pdf())
            page = pdf[0]
            bitmap = page.render(scale=PDF_RENDER_SCALE)
            pil_image = bitmap.to_pil()

            self.image_path.parent.mkdir(parents=True, exist_ok=True)
            pil_image.save(self.image_path, IMAGE_FORMAT)

            print("Saved image to path:", self.image_path)
        except Exception:
            logger.exception("Error rendering image for: %s", self.name)
            raise
        finally:
            if page is not None:
                page.close()
            if pdf is not None:
                pdf.close()

    def generate_and_save_audio(self, eleven_labs: ElevenLabs) -> None:
        """Generate audio for the transcript.

        Args:
            eleven_labs (ElevenLabs): ElevenLabs client instance.

        Raises:
            RuntimeError: If transcript is missing or audio generation fails.

        """
        if not self.transcript:
            msg = f"No transcript available for {self.name}"
            raise RuntimeError(msg)

        eleven_labs.set_text(self.transcript)
        if eleven_labs.generate_to_file(self.audio_path):
            print("Generated audio at path:", self.audio_path)
        else:
            msg = f"Failed to generate audio for {self.name}"
            raise RuntimeError(msg)

    def generate_and_save_video(self) -> None:
        """Generate video for the slide."""
        image_stream = ffmpeg.input(self.image_path, loop=1, framerate=VIDEO_FRAMERATE)
        audio_stream = ffmpeg.input(self.audio_path)

        try:
            ffmpeg.output(
                image_stream,
                audio_stream,
                filename=self.video_path,
                acodec="aac",
                vcodec="libx264",
                pix_fmt="yuv420p",
                shortest=None,
            ).run(overwrite_output=True, capture_stdout=True, capture_stderr=True)

            print("Generated video for:", self.name)

        except ffmpeg.Error:
            logger.exception("Error generating video for %s:", self.name)
            raise


class SlideBuilder:
    def __init__(self, snapshot: Snapshot, output_dir: Path) -> None:
        """Initialize SlideBuilder."""
        self.snapshot = snapshot
        self.output_dir = output_dir

    def create_intro_slide(self) -> Slide:
        """Create an introduction slide."""
        print("Generating introduction slide for snapshot")
        month_name = self.snapshot.start_at.strftime("%B")
        return Slide(
            context={
                "formatted_start": self.snapshot.start_at.strftime("%b %d"),
                "formatted_end": self.snapshot.end_at.strftime("%b %d, %Y"),
                "month_name": month_name,
            },
            name="intro",
            output_dir=self.output_dir,
            template_name="video/slides/intro.html",
            transcript=f"Hey everyone! Welcome to the OWASP Nest {month_name} Snapshot...",
        )

    def create_sponsors_slide(self) -> Slide:
        """Create a sponsors slide."""
        print("Generating sponsors slide for snapshot")

        sponsors = Sponsor.objects.values("image_url", "name").order_by("name")

        return Slide(
            context={
                "sponsors": list(sponsors),
                "title": "Our Sponsors",
            },
            output_dir=self.output_dir,
            name="sponsors",
            template_name="video/slides/sponsors.html",
            transcript="A HUGE thanks to the sponsors who make our work possible...",
        )

    def create_projects_slide(self) -> Slide:
        """Create a projects slide."""
        print("Generating projects slide for snapshot")

        new_projects = self.snapshot.new_projects.order_by("-stars_count")
        project_count = new_projects.count()

        projects_data = [
            {
                "created_at": project.created_at.strftime("%b %d, %Y"),
                "leaders": ", ".join(project.leaders_raw) if project.leaders_raw else None,
                "name": project.name,
                "stars_count": project.stars_count,
            }
            for project in new_projects
        ]

        project_names = [
            p.name.replace("OWASP ", "") for p in new_projects[:MAX_TRANSCRIPT_PROJECTS]
        ]
        formatted_project_names = (
            f"{', '.join(project_names[:-1])}, and {project_names[-1]}"
            if len(project_names) > 1
            else project_names[0]
        )

        return Slide(
            context={
                "projects": projects_data,
                "show_details": project_count <= MAX_DETAILED_PROJECTS,
                "title": f"New Projects ({project_count})",
            },
            output_dir=self.output_dir,
            name="projects",
            template_name="video/slides/projects.html",
            transcript=f"So... this time we've welcomed {project_count} new projects, "
            f"including OWASP {formatted_project_names}.",
        )

    def create_thank_you_slide(self) -> Slide:
        """Create a thank you slide."""
        print("Generating thank you slide")

        return Slide(
            context={},
            output_dir=self.output_dir,
            name="thank_you",
            template_name="video/slides/thank_you.html",
            transcript="Thanks for tuning in!... Visit OWASP Nest at nest dot owasp dot org "
            "for more community updates.... Until next time!",
        )


class Generator:
    def __init__(self) -> None:
        """Initialize Video Generator."""
        self.eleven_labs = ElevenLabs(stability=ELEVENLABS_STABILITY, style=ELEVENLABS_STYLE)
        self.slides: list[Slide] = []

    def append_slide(self, slide: Slide) -> None:
        """Append a slide to list."""
        self.slides.append(slide)

    def generate_video(self, output_path: Path) -> None:
        """Generate video."""
        for slide in self.slides:
            slide.render_and_save_image()
            slide.generate_and_save_audio(self.eleven_labs)
            slide.generate_and_save_video()

        self.merge_videos(output_path)

    def merge_videos(self, output_path: Path) -> None:
        """Combine all slide videos into final video."""
        inputs = [ffmpeg.input(str(slide.video_path)) for slide in self.slides]

        video_streams = [inp.video for inp in inputs]
        audio_streams = [inp.audio for inp in inputs]

        joined_video = ffmpeg.concat(*video_streams, v=1, a=0)
        joined_audio = ffmpeg.concat(*audio_streams, v=0, a=1)

        ffmpeg.output(joined_video, joined_audio, str(output_path)).overwrite_output().run(
            capture_stdout=True, capture_stderr=True
        )


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

        snapshot = Snapshot.objects.filter(
            key__iexact=snapshot_key, status=Snapshot.Status.COMPLETED
        ).first()

        if not snapshot:
            logger.error("No completed snapshot found for key: %s", snapshot_key)
            return

        print("Generating video for snapshot:", snapshot_key)

        slide_builder = SlideBuilder(snapshot, OUTPUT_DIR)
        generator = Generator()

        generator.append_slide(slide_builder.create_intro_slide())
        generator.append_slide(slide_builder.create_sponsors_slide())
        if snapshot.new_projects.exists():
            generator.append_slide(slide_builder.create_projects_slide())
        else:
            print("Skipping projects slide - No new projects in snapshot.")

        generator.append_slide(slide_builder.create_thank_you_slide())

        generator.generate_video(output_dir / f"{snapshot_key}_snapshot.mp4")
