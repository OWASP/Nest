from unittest.mock import MagicMock, Mock, patch

import pytest

from apps.github.models.repository import Repository
from apps.github.models.user import User
from apps.owasp.models.chapter import Chapter, Prompt


class TestChapterModel:
    @pytest.mark.parametrize(
        ("name", "country", "postal_code", "expected_geo_string"),
        [
            ("OWASP Chapter A", "USA", "12345", "Chapter A, USA, 12345"),
            ("OWASP Chapter B", "Canada", "67890", "Chapter B, Canada, 67890"),
            ("OWASP Chapter C", "", "", "Chapter C"),
            ("", "India", "11111", "India, 11111"),
        ],
    )
    def test_get_geo_string(self, name, country, postal_code, expected_geo_string):
        chapter = Chapter(name=name, country=country, postal_code=postal_code)
        assert chapter.get_geo_string() == expected_geo_string

    @pytest.mark.parametrize(
        ("suggested_location", "geo_string", "expected_location"),
        [
            ("Suggested Location A", None, "Suggested Location A"),
            ("", "Geo String B", "Geo String B"),
            (None, "Geo String C", "Geo String C"),
            ("", "", None),
        ],
    )
    def test_generate_geo_location(
        self, suggested_location, geo_string, expected_location, monkeypatch
    ):
        mock_get_location_coordinates = MagicMock(
            side_effect=lambda x: MagicMock(latitude=1, longitude=0) if x else None
        )
        monkeypatch.setattr(
            "apps.owasp.models.chapter.get_location_coordinates", mock_get_location_coordinates
        )

        chapter = Chapter(suggested_location=suggested_location)
        chapter.get_geo_string = MagicMock(return_value=geo_string)

        chapter.generate_geo_location()
        if expected_location:
            assert chapter.latitude == 1
            assert chapter.longitude == 0
        else:
            assert chapter.latitude is None
            assert chapter.longitude is None

    @pytest.mark.parametrize(
        ("is_active", "geo_string", "prompt_result", "expected_location"),
        [
            (True, "New York, USA, 10001", "Manhattan, NY", "Manhattan, NY"),
            (True, "London, UK, SW1A 1AA", "Westminster, London", "Westminster, London"),
            (True, "", "Default Location", "Default Location"),
            (False, "Paris, France", None, None),
            (True, "Tokyo, Japan", None, ""),
            (True, "Berlin, Germany", "", ""),
        ],
    )
    def test_generate_suggested_location(
        self, is_active, geo_string, prompt_result, expected_location
    ):
        mock_open_ai = MagicMock()
        mock_open_ai.set_input.return_value = mock_open_ai
        mock_open_ai.set_max_tokens.return_value = mock_open_ai
        mock_open_ai.set_prompt.return_value = mock_open_ai
        mock_open_ai.complete.return_value = prompt_result

        chapter = Chapter(is_active=is_active)
        chapter.get_geo_string = MagicMock(return_value=geo_string)

        mock_prompt = Mock()
        mock_prompt.text = "Tell me the location"
        mock_prompt_manager = Mock()
        mock_prompt_manager.get.return_value = mock_prompt

        with (
            patch.object(Prompt, "objects", mock_prompt_manager),
            patch.object(
                Prompt, "get_owasp_chapter_suggested_location", return_value=mock_prompt.text
            ),
        ):
            chapter.generate_suggested_location(open_ai=mock_open_ai)

        assert chapter.suggested_location == (expected_location or "")

        mock_open_ai.set_input.assert_called_once_with(geo_string)
        mock_open_ai.set_max_tokens.assert_called_once_with(100)
        mock_open_ai.set_prompt.assert_called_once_with("Tell me the location")
        mock_open_ai.complete.assert_called_once()

    def test_generate_suggested_location_no_prompt(self):
        """Test generate_suggested_location returns early when no prompt is available."""
        mock_open_ai = MagicMock()
        chapter = Chapter(is_active=True, suggested_location="")
        chapter.get_geo_string = MagicMock(return_value="Test Geo")

        with patch.object(Prompt, "get_owasp_chapter_suggested_location", return_value=None):
            chapter.generate_suggested_location(open_ai=mock_open_ai)

        mock_open_ai.set_input.assert_not_called()
        assert chapter.suggested_location == ""

    @pytest.mark.parametrize(
        ("name", "key", "expected_str"),
        [
            ("Test Chapter", "test-key", "Test Chapter"),
            ("", "test-key", "test-key"),
            (None, "test-key", "test-key"),
        ],
    )
    def test_str_representation(self, name, key, expected_str):
        chapter = Chapter(name=name, key=key)
        assert str(chapter) == expected_str

    @pytest.mark.parametrize(
        ("key", "expected_nest_key"),
        [
            ("www-chapter-test", "test"),
            ("www-chapter-new-york", "new-york"),
            ("www-chapter-", ""),
        ],
    )
    def test_nest_key_property(self, key, expected_nest_key):
        """Test nest_key property strips www-chapter- prefix."""
        chapter = Chapter(key=key)
        assert chapter.nest_key == expected_nest_key

    def test_nest_url_property(self):
        """Test nest_url property returns correct URL."""
        chapter = Chapter(key="www-chapter-new-york")
        with patch("apps.owasp.models.chapter.get_absolute_url") as mock_get_url:
            mock_get_url.return_value = "https://nest.owasp.org/chapters/new-york"
            url = chapter.nest_url
            mock_get_url.assert_called_once_with("chapters/new-york")
            assert url == "https://nest.owasp.org/chapters/new-york"

    @pytest.mark.parametrize(
        ("value"),
        [
            42,
        ],
    )
    def test_active_chapters_count(self, value):
        with patch.object(Chapter.objects, "filter") as mock_filter:
            mock_filter.return_value.count.return_value = value
            assert Chapter.active_chapters_count() == value
            mock_filter.assert_called_once_with(
                is_active=True,
                latitude__isnull=False,
                longitude__isnull=False,
                owasp_repository__is_empty=False,
            )

    @pytest.mark.parametrize(
        ("has_suggested_location", "has_coordinates"),
        [
            (True, True),
            (False, True),
            (True, False),
            (False, False),
        ],
    )
    def test_save_method(self, has_suggested_location, has_coordinates):
        chapter = Chapter()
        chapter.generate_suggested_location = Mock()
        chapter.generate_geo_location = Mock()

        if has_suggested_location:
            chapter.suggested_location = "Test Location"
        if has_coordinates:
            chapter.latitude = 1.1
            chapter.longitude = 2.2

        with patch("apps.owasp.models.chapter.BulkSaveModel.save"):
            chapter.save()

        if has_suggested_location:
            chapter.generate_suggested_location.assert_not_called()
        else:
            chapter.generate_suggested_location.assert_called_once()

        if has_coordinates:
            chapter.generate_geo_location.assert_not_called()
        else:
            chapter.generate_geo_location.assert_called_once()

    def test_bulk_save(self):
        mock_chapters = [Mock(id=None), Mock(id=1)]
        with patch("apps.owasp.models.chapter.BulkSaveModel.bulk_save") as mock_bulk_save:
            Chapter.bulk_save(mock_chapters, fields=["name"])
            mock_bulk_save.assert_called_once_with(Chapter, mock_chapters, fields=["name"])

    def test_from_github(self):
        owasp_repository = Repository()
        owasp_repository.created_at = "2024-01-01"
        owasp_repository.name = "Chapter Repo"
        owasp_repository.owner = User(name="OWASP")
        owasp_repository.pitch = "Nest Pitch"
        owasp_repository.tags = ["react", "python"]
        owasp_repository.title = "Nest"
        owasp_repository.updated_at = "2024-12-24"

        chapter = Chapter()
        chapter.owasp_repository = owasp_repository

        with patch(
            "apps.owasp.models.chapter.RepositoryBasedEntityModel.from_github"
        ) as mock_from_github:
            mock_from_github.side_effect = lambda instance, _: setattr(
                instance, "name", owasp_repository.title
            )
            chapter.from_github(owasp_repository)

        mock_from_github.assert_called_once_with(
            chapter,
            {
                "country": "country",
                "currency": "currency",
                "level": "level",
                "meetup_group": "meetup-group",
                "name": "title",
                "postal_code": "postal-code",
                "region": "region",
                "tags": "tags",
            },
        )

        assert chapter.created_at == owasp_repository.created_at
        assert chapter.name == owasp_repository.title
        assert chapter.updated_at == owasp_repository.updated_at

    def test_update_data_new_chapter(self):
        """Test update_data creates a new chapter when one doesn't exist."""
        mock_gh_repository = Mock()
        mock_gh_repository.name = "www-chapter-test"

        mock_repository = Mock()

        with (
            patch.object(Chapter, "objects") as mock_objects,
            patch.object(Chapter, "from_github") as mock_from_github,
            patch.object(Chapter, "save") as mock_save,
        ):
            mock_objects.get.side_effect = Chapter.DoesNotExist()

            result = Chapter.update_data(mock_gh_repository, mock_repository, save=True)

            assert result.key == "www-chapter-test"
            mock_from_github.assert_called_once_with(mock_repository)
            mock_save.assert_called_once()

    def test_update_data_existing_chapter(self):
        """Test update_data updates an existing chapter."""
        mock_gh_repository = Mock()
        mock_gh_repository.name = "www-chapter-test"

        mock_repository = Mock()
        mock_existing_chapter = Mock(spec=Chapter)

        with (
            patch.object(Chapter, "objects") as mock_objects,
            patch.object(Chapter, "from_github") as _mock_from_github,
        ):
            mock_objects.get.return_value = mock_existing_chapter

            result = Chapter.update_data(mock_gh_repository, mock_repository, save=True)

            assert result == mock_existing_chapter
            mock_existing_chapter.from_github.assert_called_once_with(mock_repository)
            mock_existing_chapter.save.assert_called_once()

    def test_update_data_no_save(self):
        """Test update_data with save=False doesn't save."""
        mock_gh_repository = Mock()
        mock_gh_repository.name = "www-chapter-new"

        mock_repository = Mock()

        with (
            patch.object(Chapter, "objects") as mock_objects,
            patch.object(Chapter, "from_github") as mock_from_github,
            patch.object(Chapter, "save") as mock_save,
        ):
            mock_objects.get.side_effect = Chapter.DoesNotExist()

            result = Chapter.update_data(mock_gh_repository, mock_repository, save=False)

            assert result.key == "www-chapter-new"
            mock_from_github.assert_called_once_with(mock_repository)
            mock_save.assert_not_called()
    
    def test_save_does_not_call_geo_location_on_zero_coords(self):
        """Verify 0.0 coordinates are treated as valid data.

        Ensure that 0.0 latitude and longitude do not trigger 
        unnecessary re-generation of geo-location data.
        """
        with patch.object(self.chapter, 'generate_geo_location') as mock_geo:
            self.chapter.latitude = 0.0
            self.chapter.longitude = 0.0
            self.chapter.save()
            
            mock_geo.assert_not_called()
