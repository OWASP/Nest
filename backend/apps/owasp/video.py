"""OWASP Community Snapshots Video Generator."""

import logging
import os
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Required to cache fonts, must be set before weasyprint is imported
os.environ["XDG_CACHE_HOME"] = str(Path(tempfile.gettempdir()) / "cache")

import ffmpeg
import pypdfium2 as pdfium
from django.db.models import QuerySet
from django.template.loader import render_to_string
from weasyprint import HTML

from apps.common.eleven_labs import ElevenLabs
from apps.github.models.release import Release
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.project import Project
from apps.owasp.models.snapshot import Snapshot
from apps.owasp.models.sponsor import Sponsor

logger = logging.getLogger(__name__)

AUDIO_CODEC = "copy"
AUDIO_EXTENSION = ".mp3"
ELEVENLABS_SPEED = 0.85
IMAGE_EXTENSION = ".png"
IMAGE_FORMAT = "PNG"
MAX_DETAILED_PROJECTS = 16
PDF_RENDER_SCALE = 2
RELEASES_LIMIT = 12
TRANSCRIPT_NAMES_LIMIT = 3
VIDEO_EXTENSION = ".mkv"
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
        """Return audio file path."""
        return self.output_dir / f"{self.name}{AUDIO_EXTENSION}"

    @property
    def image_path(self) -> Path:
        """Return image file path."""
        return self.output_dir / f"{self.name}{IMAGE_EXTENSION}"

    @property
    def video_path(self) -> Path:
        """Return video file path."""
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
        if not eleven_labs.generate_to_file(self.audio_path):
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
                acodec=AUDIO_CODEC,
                vcodec="libx264",
                pix_fmt="yuv420p",
                shortest=None,
            ).run(overwrite_output=True, capture_stdout=True, capture_stderr=True)

        except ffmpeg.Error:
            logger.exception("Error generating video for %s:", self.name)
            raise


class SlideBuilder:
    """Slide builder for community snapshot video."""

    def __init__(self, snapshots: QuerySet[Snapshot], output_dir: Path) -> None:
        """Initialize SlideBuilder."""
        self.snapshots = snapshots
        self.output_dir = output_dir

    @staticmethod
    def format_names_for_transcript(names: list[str]) -> str:
        """Format a list of names for transcript, stripping 'OWASP ' prefix."""
        cleaned = [name.replace("OWASP ", "") for name in names[:TRANSCRIPT_NAMES_LIMIT]]
        if len(cleaned) > 1:
            return f"{', '.join(cleaned[:-1])}, and {cleaned[-1]}"
        if cleaned:
            return cleaned[0]
        return ""

    def create_intro_slide(self) -> Slide:
        """Create an introduction slide."""
        first = self.snapshots.first()
        last = self.snapshots.last()
        name = first.start_at.strftime("%B") if first == last else first.start_at.strftime("%Y")

        return Slide(
            context={
                "formatted_start": first.start_at.strftime("%b %d"),
                "formatted_end": last.end_at.strftime("%b %d, %Y"),
                "name": name,
            },
            name="intro",
            output_dir=self.output_dir,
            template_name="video/slides/intro.html",
            transcript=f"Hey, everyone. Welcome to the O-WASP Nest {name} community snapshot...",
        )

    def create_sponsors_slide(self) -> Slide:
        """Create a sponsors slide."""
        sponsors = [
            {"image_url": s.image_url, "name": s.name}
            for s in sorted(
                Sponsor.objects.all(),
                key=lambda x: {
                    Sponsor.SponsorType.DIAMOND: 1,
                    Sponsor.SponsorType.PLATINUM: 2,
                    Sponsor.SponsorType.GOLD: 3,
                    Sponsor.SponsorType.SILVER: 4,
                    Sponsor.SponsorType.SUPPORTER: 5,
                    Sponsor.SponsorType.NOT_SPONSOR: 6,
                }[x.sponsor_type],
            )
        ]

        return Slide(
            context={
                "sponsors": sponsors,
                "title": "Our Sponsors",
            },
            output_dir=self.output_dir,
            name="sponsors",
            template_name="video/slides/sponsors.html",
            transcript="A HUGE thanks to the sponsors who make our work possible!",
        )

    def create_projects_slide(self) -> Slide | None:
        """Create a projects slide."""
        new_projects = (
            Project.objects.filter(snapshots__in=self.snapshots)
            .distinct()
            .order_by("-stars_count")
        )
        if not new_projects.exists():
            return None

        project_count = new_projects.count()

        projects_data = [
            {
                "contributors_count": project.contributors_count,
                "forks_count": project.forks_count,
                "leaders": ", ".join(project.leaders_raw) if project.leaders_raw else None,
                "name": project.name,
                "stars_count": project.stars_count,
            }
            for project in new_projects
        ]

        formatted_project_names = self.format_names_for_transcript([p.name for p in new_projects])

        return Slide(
            context={
                "projects": projects_data,
                "title": f"New Projects ({project_count})",
            },
            output_dir=self.output_dir,
            name="projects",
            template_name="video/slides/projects.html",
            transcript=f"So... this time we've welcomed {project_count} new projects! "
            f"including O-WASP {formatted_project_names}.",
        )

    def create_chapters_slide(self) -> Slide | None:
        """Create a chapters slide."""
        new_chapters = (
            Chapter.objects.filter(snapshots__in=self.snapshots).distinct().order_by("name")
        )
        if not new_chapters.exists():
            return None

        chapter_count = new_chapters.count()

        chapters = [
            {
                "location": f"{c.region}, {c.country}" if c.region else c.country,
                "name": c.name,
            }
            for c in new_chapters
        ]

        formatted_names = self.format_names_for_transcript([c.name for c in new_chapters])

        return Slide(
            context={
                "chapters": chapters,
                "title": f"New Chapters ({chapter_count})",
            },
            output_dir=self.output_dir,
            name="chapters",
            template_name="video/slides/chapters.html",
            transcript=f"We've also welcomed {chapter_count} new chapters! "
            f"including {formatted_names}.",
        )

    def create_releases_slide(self) -> Slide | None:
        """Create a releases slide."""
        releases = Release.objects.filter(snapshots__in=self.snapshots).distinct()
        if not releases.exists():
            return None

        project_counts: Counter = Counter()
        for release in releases:
            if not release.repository:
                continue
            project = Project.objects.filter(repositories=release.repository).first()
            if project:
                project_counts[project.name] += 1

        top_projects = project_counts.most_common(RELEASES_LIMIT)
        if not top_projects:
            return None

        max_count = top_projects[0][1] if top_projects else 1
        releases_data = [
            {
                "bar_width": int((count / max_count) * 100),
                "count": count,
                "name": name,
            }
            for name, count in top_projects
        ]

        release_count = releases.count()
        formatted_names = self.format_names_for_transcript([name for name, _ in top_projects])

        return Slide(
            context={
                "releases": releases_data,
                "title": f"New Releases ({release_count})",
            },
            output_dir=self.output_dir,
            name="releases",
            template_name="video/slides/releases.html",
            transcript=f"There were {release_count} new releases across our projects this time... "
            f"with {formatted_names} leading the way.",
        )

    def create_thank_you_slide(self) -> Slide:
        """Create a thank you slide."""
        return Slide(
            context={},
            output_dir=self.output_dir,
            name="thank_you",
            template_name="video/slides/thank_you.html",
            transcript="Thanks for tuning in!... Visit Nest at Nest dot O-WASP dot org "
            "for more community updates!... See you next time!!",
        )


class VideoGenerator:
    """Video generator for community snapshot."""

    def __init__(self) -> None:
        """Initialize Video Generator."""
        self.eleven_labs = ElevenLabs(speed=ELEVENLABS_SPEED)
        self.slides: list[Slide] = []

    def append_slide(self, slide: Slide) -> None:
        """Append a slide to list."""
        self.slides.append(slide)

    def generate_video(self, output_dir: Path, filename: str) -> Path:
        """Generate video.

        Args:
            output_dir (Path): The directory to save the video in.
            filename (str): The filename without extension.

        Returns:
            Path: The full path to the generated video.

        """
        for slide in self.slides:
            slide.render_and_save_image()
            slide.generate_and_save_audio(self.eleven_labs)
            slide.generate_and_save_video()

        output_path = output_dir / f"{filename}{VIDEO_EXTENSION}"
        self.merge_videos(output_path)

        return output_path

    def merge_videos(self, output_path: Path) -> None:
        """Combine all slide videos into final video."""
        inputs = [ffmpeg.input(str(slide.video_path)) for slide in self.slides]

        video_streams = [inp.video for inp in inputs]
        audio_streams = [inp.audio for inp in inputs]

        joined_video = ffmpeg.concat(*video_streams, v=1, a=0)
        joined_audio = ffmpeg.concat(*audio_streams, v=0, a=1)

        try:
            ffmpeg.output(joined_video, joined_audio, str(output_path)).overwrite_output().run(
                capture_stdout=True, capture_stderr=True
            )
        except ffmpeg.Error:
            logger.exception("Error merging slide videos into final output")
            raise

    def cleanup(self) -> None:
        """Remove intermediate files for all slides (audio, images, per-slide videos)."""
        for slide in self.slides:
            for path in (slide.audio_path, slide.image_path, slide.video_path):
                if path.exists():
                    path.unlink()
