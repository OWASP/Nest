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
from apps.common.open_ai import OpenAi
from apps.owasp.models.snapshot import Snapshot

logger = logging.getLogger(__name__)


@dataclass
class Slide:
    """Represents a single video slide."""

    audio_output_path: Path
    context: dict[str, Any]
    image_output_path: Path
    video_output_path: Path
    input: str
    name: str
    template_name: str

    def render_and_save(self) -> None:
        """Render an HTML template as an image."""
        page = None
        pdf = None
        try:
            html_content = render_to_string(self.template_name, self.context)

            print("Rendering slide image")

            html = HTML(string=html_content)

            pdf = pdfium.PdfDocument(html.write_pdf())
            page = pdf[0]
            bitmap = page.render(scale=2)
            pil_image = bitmap.to_pil()

            self.image_output_path.parent.mkdir(parents=True, exist_ok=True)
            pil_image.save(self.image_output_path, "PNG")

            print("Saved image to path:", self.image_output_path)
        except Exception:
            logger.exception("Error rendering image for: %s", self.name)
            raise
        finally:
            if page is not None:
                page.close()
            if pdf is not None:
                pdf.close()

    def generate_transcript(self, open_ai: OpenAi) -> None:
        """Generate a transcript."""
        print("Prompt:", self.input)
        prompt = """
        You are a scriptwriter for a tech presentation.
        Your task is to generate a script for a presentation slide.
        The script should be simple and direct.
        Do not add any extra words, introduction or conclusion.
        """
        open_ai.set_prompt(prompt)
        open_ai.set_input(self.input)

        try:
            self.transcript = open_ai.complete()
            print("Generated slide transcript:", self.transcript)
        except Exception:
            logger.exception("Error generating transcript for %s", self.name)
            raise

    def generate_audio(self, eleven_labs: ElevenLabs) -> None:
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
        if eleven_labs.generate_to_file(self.audio_output_path):
            print("Generated audio at path:", self.audio_output_path)
        else:
            msg = f"Failed to generate audio for {self.name}"
            raise RuntimeError(msg)

    def generate_video(self) -> None:
        """Generate video for the slide."""
        image_stream = ffmpeg.input(self.image_output_path, loop=1, framerate=60)
        audio_stream = ffmpeg.input(self.audio_output_path)

        try:
            ffmpeg.output(
                image_stream,
                audio_stream,
                filename=self.video_output_path,
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
    def __init__(self, snapshot, output_dir: Path) -> None:
        """Initialize SlideBuilder."""
        self.snapshot = snapshot
        self.output_dir = output_dir

    def create_intro_slide(self) -> Slide:
        """Create an introduction slide."""
        print("Generating introduction slide for snapshot")
        month_name = self.snapshot.start_at.strftime("%B")
        return Slide(
            audio_output_path=self.output_dir / "01_intro.mp3",
            context={
                "formatted_start": self.snapshot.start_at.strftime("%b %d"),
                "formatted_end": self.snapshot.end_at.strftime("%b %d, %Y"),
                "month_name": month_name,
            },
            image_output_path=self.output_dir / "01_intro.png",
            input=f"Hello everyone! welcome to the OWASP Nest {month_name} Snapshot",
            name="Intro Slide",
            template_name="video/slides/intro.html",
            video_output_path=self.output_dir / "01_intro.mp4",
        )


class Generator:
    def __init__(self) -> None:
        """Initialize Video Generator."""
        self.eleven_labs = ElevenLabs()
        self.open_ai = OpenAi()
        self.slides: list[Slide] = []

    def append_slide(self, slide: Slide) -> None:
        """Append a slide to list."""
        self.slides.append(slide)

    def generate_video(self) -> None:
        """Generate video."""
        for slide in self.slides:
            slide.render_and_save()
            slide.generate_transcript(self.open_ai)
            slide.generate_audio(self.eleven_labs)
            slide.generate_video()


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
            help="Directory to save generated files",
        )
        parser.add_argument(
            "--snapshot-key",
            required=True,
            type=str,
            help="Snapshot key (e.g., '2025-06' for month or '2025' for year)",
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

        slide_builder = SlideBuilder(snapshot, output_dir)
        generator = Generator()

        generator.append_slide(slide_builder.create_intro_slide())

        generator.generate_video()
