from unittest.mock import MagicMock, Mock, patch

import pytest

from apps.github.models.repository import Repository
from apps.owasp.models.chapter import Chapter, Prompt


@pytest.mark.parametrize(
    ("name", "country", "postal_code", "expected_geo_string"),
    [
        ("OWASP Chapter A", "USA", "12345", "Chapter A, USA, 12345"),
        ("OWASP Chapter B", "Canada", "67890", "Chapter B, Canada, 67890"),
        ("OWASP Chapter C", "", "", "Chapter C"),
        ("", "India", "11111", "India, 11111"),
    ],
)
def test_get_geo_string(name, country, postal_code, expected_geo_string):
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
def test_generate_geo_location(suggested_location, geo_string, expected_location, monkeypatch):
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
        (False, "Paris, France", None, None),  # Inactive chapter
        (True, "Tokyo, Japan", None, ""),  # None result from OpenAI
        (True, "Berlin, Germany", "", ""),  # Empty string from OpenAI
    ],
)
def test_generate_suggested_location(is_active, geo_string, prompt_result, expected_location):
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

    with patch.object(Prompt, "objects", mock_prompt_manager), patch.object(
        Prompt, "get_owasp_chapter_suggested_location", return_value=mock_prompt.text
    ):
        chapter.generate_suggested_location(open_ai=mock_open_ai)

    assert chapter.suggested_location == (expected_location or "")

    if is_active:
        mock_open_ai.set_input.assert_called_once_with(geo_string)
        mock_open_ai.set_max_tokens.assert_called_once_with(100)
        mock_open_ai.set_prompt.assert_called_once_with("Tell me the location")
        mock_open_ai.complete.assert_called_once()
    else:
        mock_open_ai.set_input.assert_not_called()
        mock_open_ai.set_max_tokens.assert_not_called()
        mock_open_ai.set_prompt.assert_not_called()
        mock_open_ai.complete.assert_not_called()


@pytest.mark.parametrize(
    ("name", "key", "expected_str"),
    [
        ("Test Chapter", "test-key", "Test Chapter"),
        ("", "test-key", "test-key"),
        (None, "test-key", "test-key"),
    ],
)
def test_str_representation(name, key, expected_str):
    chapter = Chapter(name=name, key=key)
    assert str(chapter) == expected_str


@pytest.mark.parametrize(
    ("value"),
    [
        42,
    ],
)
def test_active_chapters_count(value):
    with patch("apps.common.index.IndexBase.get_total_count") as mock_count:
        mock_count.return_value = value
        assert Chapter.active_chapters_count() == value
        mock_count.assert_called_once_with("chapters")


@pytest.mark.parametrize(
    ("has_suggested_location", "has_coordinates"),
    [
        (True, True),
        (False, True),
        (True, False),
        (False, False),
    ],
)
def test_save_method(has_suggested_location, has_coordinates):
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

    if not has_suggested_location:
        chapter.generate_suggested_location.assert_called_once()
    else:
        chapter.generate_suggested_location.assert_not_called()

    if not has_coordinates:
        chapter.generate_geo_location.assert_called_once()
    else:
        chapter.generate_geo_location.assert_not_called()


def test_bulk_save():
    mock_chapters = [Mock(id=None), Mock(id=1)]
    with patch("apps.owasp.models.chapter.BulkSaveModel.bulk_save") as mock_bulk_save:
        Chapter.bulk_save(mock_chapters, fields=["name"])
        mock_bulk_save.assert_called_once_with(Chapter, mock_chapters, fields=["name"])


def test_from_github():
    repository_mock = Repository()
    repository_mock.name = "Test Repo"
    repository_mock.created_at = "2024-01-01"
    repository_mock.updated_at = "2024-12-24"
    repository_mock.title = "Nest"
    repository_mock.pitch = "Nest Pitch"
    repository_mock.tags = ["react", "python"]

    chapter = Chapter()

    with patch(
        "apps.owasp.models.chapter.RepositoryBasedEntityModel.from_github"
    ) as mock_from_github:
        mock_from_github.side_effect = lambda instance, _, repo: setattr(
            instance, "name", repo.title
        )

        chapter.from_github(repository_mock)

    assert chapter.created_at == repository_mock.created_at
    assert chapter.updated_at == repository_mock.updated_at
    assert chapter.owasp_repository == repository_mock

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
        repository_mock,
    )

    assert chapter.name == repository_mock.title
