from unittest import mock

import pytest

from apps.owasp.management.commands.owasp_enrich_chapters import (
    Chapter,
    Command,
    Prompt,
)


class TestOwaspEnrichChapters:
    @pytest.fixture
    def command(self):
        return Command()

    @pytest.fixture
    def mock_chapter(self):
        chapter = mock.Mock(spec=Chapter)
        chapter.owasp_url = "https://owasp.org/www-chapter-test"
        chapter.summary = None
        chapter.suggested_location = None
        chapter.latitude = None
        chapter.longitude = None
        return chapter

    @pytest.mark.parametrize(
        ("offset", "chapters", "latitude", "longitude"),
        [
            (0, 3, 12.43, 43.35),
            (2, 5, 31.76, 12.87),
            (0, 6, 45.23, 84.23),
            (1, 8, 75.84, 85.06),
        ],
    )
    @mock.patch.dict("os.environ", {"GEO_API_KEY": "test-token"})
    @mock.patch.object(Chapter, "bulk_save", autospec=True)
    def test_handle(
        self, mock_bulk_save, command, mock_chapter, offset, chapters, latitude, longitude
    ):
        mock_prompt = mock.Mock()
        mock_prompt.get_owasp_chapter_summary.return_value = "summary prompt"

        mock_chapter.generate_summary.side_effect = lambda **_: setattr(
            mock_chapter, "summary", "Generated summary"
        )
        mock_chapter.generate_suggested_location.side_effect = lambda: setattr(
            mock_chapter, "suggested_location", "Suggested location"
        )
        mock_chapter.generate_geo_location.side_effect = lambda: (
            setattr(mock_chapter, "latitude", latitude)
            or setattr(mock_chapter, "longitude", longitude)
        )

        mock_chapters_list = [mock_chapter] * chapters

        mock_active_chapters = mock.MagicMock()
        mock_active_chapters.__iter__.return_value = iter(mock_chapters_list)
        mock_active_chapters.count.return_value = len(mock_chapters_list)
        mock_active_chapters.__getitem__.side_effect = lambda idx: (
            mock_chapters_list[idx.start : idx.stop]
            if isinstance(idx, slice)
            else mock_chapters_list[idx]
        )
        mock_active_chapters.without_geo_data.order_by.return_value = mock_active_chapters

        with (
            mock.patch.object(Chapter, "active_chapters", mock_active_chapters),
            mock.patch.object(
                Prompt, "get_owasp_chapter_summary", mock_prompt.get_owasp_chapter_summary
            ),
            mock.patch("builtins.print") as mock_print,
            mock.patch("time.sleep", return_value=None),
        ):
            command.handle(offset=offset)

        mock_active_chapters.count.assert_called_once()

        assert mock_bulk_save.called

        assert mock_print.call_count == len(mock_chapters_list) - offset

        for call in mock_print.call_args_list:
            args, _ = call
            assert "https://owasp.org/www-chapter-test" in args[0]

        for chapter in mock_chapters_list:
            assert chapter.summary == "Generated summary"
            assert chapter.suggested_location == "Suggested location"
            assert chapter.latitude == latitude
            assert chapter.longitude == longitude
