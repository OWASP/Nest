from unittest.mock import MagicMock, Mock, patch

import ffmpeg
import pytest

from apps.owasp.video import (
    AUDIO_EXTENSION,
    IMAGE_EXTENSION,
    VIDEO_EXTENSION,
    Slide,
    SlideBuilder,
    VideoGenerator,
)


class TestSlide:
    @pytest.fixture
    def slide(self, tmp_path):
        """Fixture to provide a sample slide."""
        return Slide(
            context={"title": "Test Slide"},
            name="test_slide",
            output_dir=tmp_path,
            template_name="slides/intro.jinja",
            transcript="Test transcript",
        )

    def test_audio_path(self, slide, tmp_path):
        """Test audio_path property returns correct path."""
        expected = tmp_path / f"test_slide.{AUDIO_EXTENSION}"
        assert slide.audio_path == expected

    def test_image_path(self, slide, tmp_path):
        """Test image_path property returns correct path."""
        expected = tmp_path / f"test_slide.{IMAGE_EXTENSION}"
        assert slide.image_path == expected

    def test_video_path(self, slide, tmp_path):
        """Test video_path property returns correct path."""
        expected = tmp_path / f"test_slide.{VIDEO_EXTENSION}"
        assert slide.video_path == expected

    @patch("apps.owasp.video.pdfium.PdfDocument")
    @patch("apps.owasp.video.HTML")
    @patch("apps.owasp.video.video_env")
    def test_render_and_save_image_success(
        self, mock_video_env, mock_html, mock_pdfium, slide, tmp_path
    ):
        """Test render_and_save_image creates image file."""
        mock_template = Mock()
        mock_template.render.return_value = "<html></html>"
        mock_video_env.get_template.return_value = mock_template
        mock_html.return_value.write_pdf.return_value = b"pdf_content"

        mock_bitmap = Mock()
        mock_pil_image = Mock()
        mock_bitmap.to_pil.return_value = mock_pil_image

        mock_page = Mock()
        mock_page.render.return_value = mock_bitmap

        mock_pdf = Mock()
        mock_pdf.__getitem__ = Mock(return_value=mock_page)
        mock_pdfium.return_value = mock_pdf

        slide.render_and_save_image()

        mock_video_env.get_template.assert_called_once_with(slide.template_name)
        mock_template.render.assert_called_once_with(slide.context)
        mock_pil_image.save.assert_called_once()
        mock_page.close.assert_called_once()
        mock_pdf.close.assert_called_once()

    def test_generate_and_save_audio_generation_fails(self, slide):
        """Test generate_and_save_audio raises error when generation fails."""
        eleven_labs = Mock()
        eleven_labs.generate.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            slide.generate_and_save_audio(eleven_labs)

    def test_generate_and_save_audio_success(self, slide):
        """Test generate_and_save_audio succeeds."""
        eleven_labs = Mock()
        eleven_labs.generate.return_value = b"audio_data"

        slide.generate_and_save_audio(eleven_labs)

        eleven_labs.set_text.assert_called_once_with(slide.transcript)
        eleven_labs.generate.assert_called_once()
        eleven_labs.save.assert_called_once_with(b"audio_data", slide.audio_path)

    @patch("apps.owasp.video.ffmpeg")
    def test_generate_and_save_video_success(self, mock_ffmpeg, slide):
        """Test generate_and_save_video succeeds."""
        mock_input = Mock()
        mock_ffmpeg.input.return_value = mock_input
        mock_output = Mock()
        mock_ffmpeg.output.return_value = mock_output

        slide.generate_and_save_video()

        assert mock_ffmpeg.input.call_count == 2
        mock_ffmpeg.output.assert_called_once()

    @patch("apps.owasp.video.logger")
    @patch("apps.owasp.video.ffmpeg")
    def test_generate_and_save_video_exception(self, mock_ffmpeg, mock_logger, slide):
        """Test generate_and_save_video logs exception on error."""
        mock_ffmpeg.output.return_value.run.side_effect = ffmpeg.Error(
            "ffmpeg", "stdout", "stderr"
        )
        mock_ffmpeg.Error = ffmpeg.Error

        with pytest.raises(ffmpeg.Error):
            slide.generate_and_save_video()

        mock_logger.exception.assert_called_once()

    @patch("apps.owasp.video.pdfium.PdfDocument")
    @patch("apps.owasp.video.HTML")
    @patch("apps.owasp.video.video_env")
    def test_render_and_save_image_render_error(
        self, mock_video_env, mock_html, mock_pdfium, slide
    ):
        """Test render_and_save_image handles render error."""
        mock_template = Mock()
        mock_video_env.get_template.return_value = mock_template
        mock_html.return_value.write_pdf.side_effect = Exception("Render Error")

        with pytest.raises(Exception, match="Render Error"):
            slide.render_and_save_image()

    @patch("apps.owasp.video.pdfium.PdfDocument")
    @patch("apps.owasp.video.HTML")
    @patch("apps.owasp.video.video_env")
    def test_render_and_save_image_page_error_closes_pdf(
        self, mock_video_env, mock_html, mock_pdfium, slide
    ):
        """Test render_and_save_image ensures PDF is closed on page error."""
        mock_template = Mock()
        mock_video_env.get_template.return_value = mock_template
        mock_pdf = MagicMock()
        mock_pdfium.return_value = mock_pdf
        mock_pdf.__getitem__.side_effect = Exception("Page Error")

        with pytest.raises(Exception, match="Page Error"):
            slide.render_and_save_image()

        mock_pdf.close.assert_called_once()


class TestSlideBuilder:
    @pytest.fixture
    def mock_snapshots(self):
        """Fixture to provide mock snapshots queryset."""
        mock_qs = MagicMock()
        mock_snapshot = Mock()
        mock_snapshot.start_at.strftime.return_value = "January"
        mock_snapshot.end_at.strftime.return_value = "Jan 31, 2024"
        mock_qs.first.return_value = mock_snapshot
        mock_qs.last.return_value = mock_snapshot
        return mock_qs

    @pytest.fixture
    def slide_builder(self, mock_snapshots, tmp_path):
        """Fixture to provide a SlideBuilder instance."""
        return SlideBuilder(mock_snapshots, output_dir=tmp_path)

    def test_init(self, slide_builder, mock_snapshots):
        """Test SlideBuilder initialization."""
        assert slide_builder.snapshots == mock_snapshots

    @pytest.mark.parametrize(
        ("names", "expected"),
        [
            (["OWASP Project A"], "Project A"),
            (["OWASP A", "OWASP B"], "A, and B"),
            (["OWASP A", "OWASP B", "OWASP C"], "A, B, and C"),
            (["OWASP A", "OWASP B", "OWASP C", "OWASP D"], "A, B, and C"),
            ([], ""),
        ],
    )
    def test_format_names_for_transcript(self, names, expected):
        """Test format_names_for_transcript formats names correctly."""
        result = SlideBuilder.format_names_for_transcript(names)
        assert result == expected

    def test_add_intro_slide(self, slide_builder):
        """Test add_intro_slide returns a Slide."""
        slide = slide_builder.add_intro_slide()

        assert isinstance(slide, Slide)
        assert slide.name == "intro"
        assert slide.template_name == "slides/intro.jinja"
        assert slide.transcript is not None

    def test_add_intro_slide_multi_snapshot(self, tmp_path):
        """Test add_intro_slide with different first and last snapshots."""
        mock_qs = MagicMock()
        first_snapshot = Mock()
        first_snapshot.start_at.strftime.side_effect = lambda fmt: (
            "2024" if fmt == "%Y" else "Jan 01"
        )
        last_snapshot = Mock()
        last_snapshot.end_at.strftime.return_value = "Dec 31, 2024"
        mock_qs.first.return_value = first_snapshot
        mock_qs.last.return_value = last_snapshot

        slide_builder = SlideBuilder(mock_qs, output_dir=tmp_path)
        slide = slide_builder.add_intro_slide()

        assert isinstance(slide, Slide)
        assert slide.transcript
        assert "2024" in slide.transcript

    @patch("apps.owasp.video.Sponsor.objects")
    def test_add_sponsors_slide(self, mock_sponsor_objects, slide_builder):
        """Test add_sponsors_slide returns a Slide."""
        mock_sponsor_objects.all.return_value = []

        slide = slide_builder.add_sponsors_slide()

        assert isinstance(slide, Slide)
        assert slide.name == "sponsors"

    @patch("apps.owasp.video.Project.objects")
    def test_add_projects_slide_no_projects(self, mock_project_objects, slide_builder):
        """Test add_projects_slide returns None when no projects."""
        mock_qs = MagicMock()
        mock_qs.exists.return_value = False
        mock_project_objects.filter.return_value.distinct.return_value.order_by.return_value = (
            mock_qs
        )

        result = slide_builder.add_projects_slide()

        assert result is None

    @patch("apps.owasp.video.Project.objects")
    def test_add_projects_slide_with_projects(self, mock_project_objects, slide_builder):
        """Test add_projects_slide returns Slide when projects exist."""
        mock_project = Mock()
        mock_project.name = "Test Project"
        mock_project.stars_count = 100
        mock_project.forks_count = 50
        mock_project.contributors_count = 10
        mock_project.leaders_raw = ["Leader 1"]

        mock_qs = MagicMock()
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 1
        mock_qs.__iter__ = Mock(return_value=iter([mock_project]))
        mock_project_objects.filter.return_value.distinct.return_value.order_by.return_value = (
            mock_qs
        )

        result = slide_builder.add_projects_slide()

        assert isinstance(result, Slide)
        assert result.name == "projects"

    @patch("apps.owasp.video.Chapter.objects")
    def test_add_chapters_slide_no_chapters(self, mock_chapter_objects, slide_builder):
        """Test add_chapters_slide returns None when no chapters."""
        mock_qs = MagicMock()
        mock_qs.exists.return_value = False
        mock_chapter_objects.filter.return_value.distinct.return_value.order_by.return_value = (
            mock_qs
        )

        result = slide_builder.add_chapters_slide()

        assert result is None

    @patch("apps.owasp.video.Chapter.objects")
    def test_add_chapters_slide_with_chapters(self, mock_chapter_objects, slide_builder):
        """Test add_chapters_slide returns Slide when chapters exist."""
        mock_chapter = Mock()
        mock_chapter.name = "Test Chapter"
        mock_chapter.suggested_location = "California, USA"

        mock_qs = MagicMock()
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 1
        mock_qs.__iter__ = Mock(return_value=iter([mock_chapter]))
        mock_chapter_objects.filter.return_value.distinct.return_value.order_by.return_value = (
            mock_qs
        )

        result = slide_builder.add_chapters_slide()

        assert isinstance(result, Slide)
        assert result.name == "chapters"

    @patch("apps.owasp.video.Project.objects")
    @patch("apps.owasp.video.Release.objects")
    def test_add_releases_slide_no_releases(
        self, mock_release_objects, mock_project_objects, slide_builder
    ):
        """Test add_releases_slide returns None when no releases."""
        mock_qs = MagicMock()
        mock_qs.exists.return_value = False
        mock_release_objects.filter.return_value.distinct.return_value = mock_qs

        result = slide_builder.add_releases_slide()

        assert result is None

    @patch("apps.owasp.video.Project.objects")
    @patch("apps.owasp.video.Release.objects")
    def test_add_releases_slide_with_releases(
        self, mock_release_objects, mock_project_objects, slide_builder
    ):
        """Test add_releases_slide returns Slide when releases exist."""
        mock_release = Mock()
        mock_repository = Mock()
        mock_release.repository = mock_repository

        mock_project = Mock()
        mock_project.name = "Test Project"

        mock_release_qs = MagicMock()
        mock_release_qs.exists.return_value = True
        mock_release_qs.count.return_value = 5
        mock_release_qs.__iter__ = Mock(return_value=iter([mock_release]))
        mock_release_objects.filter.return_value.distinct.return_value = mock_release_qs

        mock_project_qs = MagicMock()
        mock_project_qs.first.return_value = mock_project
        mock_project_objects.filter.return_value = mock_project_qs

        result = slide_builder.add_releases_slide()

        assert isinstance(result, Slide)
        assert result.name == "releases"

    def test_add_thank_you_slide(self, slide_builder):
        """Test add_thank_you_slide returns a Slide."""
        slide = slide_builder.add_thank_you_slide()

        assert isinstance(slide, Slide)
        assert slide.name == "thank_you"
        assert slide.template_name == "slides/thank_you.jinja"

    @patch("apps.owasp.video.Project.objects")
    @patch("apps.owasp.video.Release.objects")
    def test_add_releases_slide_edge_cases(
        self, mock_release_objects, mock_project_objects, slide_builder
    ):
        """Test add_releases_slide edge cases (no repo, no project)."""
        release_no_repo = Mock()
        release_no_repo.repository = None
        release_no_project = Mock()
        release_no_project.repository = Mock()

        mock_release_qs = MagicMock()
        mock_release_qs.exists.return_value = True
        mock_release_qs.count.return_value = 2
        mock_release_qs.__iter__ = Mock(return_value=iter([release_no_repo, release_no_project]))
        mock_release_objects.filter.return_value.distinct.return_value = mock_release_qs
        mock_project_objects.filter.return_value.first.return_value = None
        result = slide_builder.add_releases_slide()
        assert result is None


class TestVideoGenerator:
    @pytest.fixture
    def generator(self):
        """Fixture to provide a VideoGenerator instance."""
        with patch("apps.owasp.video.ElevenLabs"):
            return VideoGenerator()

    def test_init(self, generator):
        """Test VideoGenerator initialization."""
        assert generator.slides == []

    def test_append_slide(self, generator):
        """Test append_slide adds slide to list."""
        slide = Mock()
        generator.append_slide(slide)

        assert len(generator.slides) == 1
        assert generator.slides[0] == slide

    def test_generate_video(self, generator, tmp_path):
        """Test generate_video calls methods on all slides."""
        slide1 = Mock()
        slide2 = Mock()
        generator.slides = [slide1, slide2]

        with patch.object(generator, "merge_videos"):
            generator.generate_video(tmp_path, "output")

        slide1.render_and_save_image.assert_called_once()
        slide1.generate_and_save_audio.assert_called_once()
        slide1.generate_and_save_video.assert_called_once()
        slide2.render_and_save_image.assert_called_once()

    @patch("apps.owasp.video.ffmpeg")
    def test_merge_videos(self, mock_ffmpeg, generator, tmp_path):
        """Test merge_videos combines slide videos."""
        slide1 = Mock()
        slide1.video_path = tmp_path / "slide1.mp4"
        slide2 = Mock()
        slide2.video_path = tmp_path / "slide2.mp4"
        generator.slides = [slide1, slide2]

        mock_input = Mock()
        mock_input.video = Mock()
        mock_input.audio = Mock()
        mock_ffmpeg.input.return_value = mock_input
        mock_ffmpeg.concat.return_value = Mock()
        mock_ffmpeg.output.return_value.overwrite_output.return_value.run = Mock()

        generator.merge_videos(tmp_path / "output.mp4")

        assert mock_ffmpeg.input.call_count == 2
        assert mock_ffmpeg.concat.call_count == 2

    @patch("apps.owasp.video.logger")
    @patch("apps.owasp.video.ffmpeg")
    def test_merge_videos_exception(self, mock_ffmpeg, mock_logger, generator, tmp_path):
        """Test merge_videos logs exception on error."""
        slide = Mock()
        slide.video_path = tmp_path / "slide.mp4"
        generator.slides = [slide]

        mock_input = Mock()
        mock_input.video = Mock()
        mock_input.audio = Mock()
        mock_ffmpeg.input.return_value = mock_input
        mock_ffmpeg.concat.return_value = Mock()
        mock_ffmpeg.output.return_value.overwrite_output.return_value.run.side_effect = (
            ffmpeg.Error("ffmpeg", "stdout", "stderr")
        )
        mock_ffmpeg.Error = ffmpeg.Error

        with pytest.raises(ffmpeg.Error):
            generator.merge_videos(tmp_path / "output.mp4")

        mock_logger.exception.assert_called_once()

    def test_cleanup(self, generator, tmp_path):
        """Test cleanup removes temporary files."""
        slide = Mock()
        slide.audio_path = Mock()
        slide.image_path = Mock()
        slide.video_path = Mock()
        slide.audio_path.exists.return_value = True
        slide.image_path.exists.return_value = True
        slide.video_path.exists.return_value = False

        generator.slides = [slide]
        generator.cleanup()

        slide.audio_path.unlink.assert_called_once()
        slide.image_path.unlink.assert_called_once()
        slide.video_path.unlink.assert_not_called()
