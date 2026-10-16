from argparse import ArgumentParser
from contextlib import nullcontext
from http import HTTPStatus
from unittest import mock

import pytest
import requests

from apps.owasp.management.commands.owasp_sync_chapters import Chapter, Command


def chapter_record(**overrides):
    record = {
        "city": "London",
        "country": "United Kingdom",
        "is_active": True,
        "name": "OWASP London",
        "region": "Europe",
        "slug": "london",
    }
    record.update(overrides)
    return record


def response(chapters, *, status_code=HTTPStatus.OK):
    payload = mock.Mock()
    payload.status_code = status_code
    payload.headers = {}
    payload.json.return_value = {"chapters": chapters}
    return payload


class TestOwaspSyncChapters:
    @pytest.fixture(autouse=True)
    def database_transaction(self, monkeypatch):
        """Keep these tests off the database while the command uses a transaction."""
        monkeypatch.setattr(
            "apps.owasp.management.commands.owasp_sync_chapters.transaction.atomic",
            nullcontext,
        )

    @pytest.fixture
    def command(self):
        return Command()

    def test_add_arguments(self, command):
        """Test add_arguments adds expected arguments."""
        parser = ArgumentParser()
        command.add_arguments(parser)
        args = parser.parse_args([])
        assert args.offset == 0

    @pytest.fixture
    def mock_chapter(self):
        chapter = mock.Mock(spec=Chapter)
        chapter.id = 1
        chapter.key = "www-chapter-london"
        chapter.name = "Old name"
        chapter.owasp_url = "https://owasp.org/www-chapter-london"
        chapter.github_url = "https://github.com/owasp/www-chapter-london"
        chapter.get_related_url.side_effect = lambda url, **_: url
        chapter.leaders_raw = ["Existing Leader"]
        chapter.related_urls = ["https://example.com/existing"]
        chapter.is_active = True
        return chapter

    @mock.patch.object(Chapter, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_renames_chapter_to_the_website_slug(
        self, mock_get, mock_bulk_save, command, mock_chapter
    ):
        """Test a www-chapter key is renamed to the website slug."""
        mock_get.return_value = response(
            [
                chapter_record(
                    description="<p>Local meetings.</p>",
                    leadership_team=[{"contact": "sam@owasp.org", "name": "Sam Stepanyan"}],
                    meetup_url="https://www.meetup.com/OWASP-London/",
                )
            ]
        )

        with mock.patch.object(Chapter, "objects") as mock_objects:
            mock_objects.all.return_value = [mock_chapter]
            command.stdout = mock.MagicMock()
            command.handle(offset=0)

        assert mock_chapter.key == "london"
        assert mock_chapter.name == "OWASP London"
        assert mock_chapter.description == "Local meetings."
        assert mock_chapter.country == "United Kingdom"
        assert mock_chapter.region == "Europe"
        assert mock_chapter.is_active is True
        assert mock_chapter.leaders_raw == ["Sam Stepanyan"]
        mock_chapter.sync_leaders.assert_called_once_with({"Sam Stepanyan": "sam@owasp.org"})
        assert "https://www.meetup.com/OWASP-London" in mock_chapter.related_urls
        mock_chapter.deactivate.assert_not_called()
        assert mock_bulk_save.called

    @mock.patch.object(Chapter, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_preserves_leaders_when_source_has_none(
        self, mock_get, mock_bulk_save, command, mock_chapter
    ):
        """Test a catalog record without leaders leaves stored leaders unchanged."""
        mock_get.return_value = response([chapter_record()])

        with mock.patch.object(Chapter, "objects") as mock_objects:
            mock_objects.all.return_value = [mock_chapter]
            command.stdout = mock.MagicMock()
            command.handle(offset=0)

        assert mock_chapter.leaders_raw == ["Existing Leader"]
        assert mock_chapter.related_urls == []
        mock_chapter.sync_leaders.assert_not_called()

    @mock.patch.object(Chapter, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_creates_chapter_with_slug_key(self, mock_get, mock_bulk_save, command):
        """Test a chapter Nest has never seen is stored under the website slug."""
        mock_get.return_value = response([chapter_record()])

        with mock.patch.object(Chapter, "objects") as mock_objects:
            mock_objects.all.return_value = []
            command.stdout = mock.MagicMock()
            command.handle(offset=0)

        created = mock_bulk_save.call_args_list[0].args[0][0]
        assert created.key == "london"
        assert created.name == "OWASP London"
        assert created.country == "United Kingdom"

    @mock.patch.object(Chapter, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_deactivates_chapter_missing_from_catalog(
        self, mock_get, mock_bulk_save, command, mock_chapter
    ):
        """Test an active local chapter absent from a complete catalog is deactivated."""
        mock_get.return_value = response([chapter_record()])
        stale = mock.Mock(spec=Chapter)
        stale.id = 2
        stale.key = "www-chapter-retired"
        stale.is_active = True

        with mock.patch.object(Chapter, "objects") as mock_objects:
            mock_objects.all.return_value = [mock_chapter, stale]
            command.stdout = mock.MagicMock()
            command.handle(offset=0)

        stale.deactivate.assert_called_once()
        mock_chapter.deactivate.assert_not_called()

    @mock.patch.object(Chapter, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_leaves_chapters_unchanged_when_fetch_fails(
        self, mock_get, mock_bulk_save, command, mock_chapter
    ):
        """Test a failed catalog request does not write or deactivate chapters."""
        mock_get.side_effect = requests.exceptions.RequestException("offline")

        with mock.patch.object(Chapter, "objects") as mock_objects:
            mock_objects.all.return_value = [mock_chapter]
            command.stdout = mock.MagicMock()
            command.handle(offset=0)

        mock_bulk_save.assert_not_called()
        mock_chapter.deactivate.assert_not_called()
        mock_chapter.sync_leaders.assert_not_called()
        assert mock_chapter.leaders_raw == ["Existing Leader"]

    @mock.patch.object(Chapter, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_marks_chapter_inactive_when_is_active_is_missing(
        self, mock_get, mock_bulk_save, command, mock_chapter
    ):
        """Test a catalog record without is_active deactivates the chapter."""
        record = chapter_record()
        record.pop("is_active")
        mock_get.return_value = response([record])

        with mock.patch.object(Chapter, "objects") as mock_objects:
            mock_objects.all.return_value = [mock_chapter]
            command.stdout = mock.MagicMock()
            command.handle(offset=0)

        assert mock_chapter.is_active is False

    @mock.patch.object(Chapter, "bulk_save", autospec=True)
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_keeps_the_slug_row_when_a_legacy_key_also_exists(
        self, mock_get, mock_bulk_save, command, mock_chapter
    ):
        """Test the website slug is the chapter that stays active."""
        mock_get.return_value = response([chapter_record()])
        slug_chapter = mock.Mock(spec=Chapter)
        slug_chapter.pk = 2
        slug_chapter.id = 2
        slug_chapter.key = "london"
        slug_chapter.name = "OWASP London"
        slug_chapter.owasp_url = "https://owasp.org/chapters/london"
        slug_chapter.github_url = "https://github.com/owasp/london"
        slug_chapter.get_related_url.side_effect = lambda url, **_: url
        slug_chapter.is_active = True

        with mock.patch.object(Chapter, "objects") as mock_objects:
            mock_objects.all.return_value = [mock_chapter, slug_chapter]
            command.stdout = mock.MagicMock()
            command.handle(offset=0)

        assert slug_chapter.key == "london"
        slug_chapter.delete.assert_not_called()
        slug_chapter.deactivate.assert_not_called()
        mock_chapter.deactivate.assert_called_once()
