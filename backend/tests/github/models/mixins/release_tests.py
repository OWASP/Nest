from datetime import datetime, timezone
from unittest.mock import MagicMock
import pytest

from apps.github.models.mixins.release import ReleaseIndexMixin


class MockModel(ReleaseIndexMixin):
    def __init__(self):
        self.author = MagicMock()

        self.author.avatar_url="https://example.com/avatar.png"
        self.author.login="test_user"
        self.author.name="Test User"
        
        self.repository = MagicMock(
            path="mock/repository",
            project=MagicMock(nest_key="mock/project"),
        )
        self.created_at = datetime(2023, 1, 1, tzinfo=timezone.utc)
        self.published_at = datetime(2023, 6, 1, tzinfo=timezone.utc)
        self.description = "This is a long description that should be truncated for indexing purposes."
        self.is_pre_release = True
        self.name = "Release v1.0.0"
        self.tag_name = "v1.0.0"


@pytest.mark.parametrize(
    ("attr", "expected"),
    [
        ("idx_author", [{"avatar_url": "https://example.com/avatar.png", "login": "test_user", "name": "Test User"}]),
        ("idx_created_at", datetime(2023, 1, 1, tzinfo=timezone.utc).timestamp()),
        ("idx_description", "This is a long description that should be truncated for indexing purposes."),
        ("idx_is_pre_release", True),
        ("idx_name", "Release v1.0.0"),
        ("idx_project", "mock/project"),
        ("idx_published_at", datetime(2023, 6, 1, tzinfo=timezone.utc).timestamp()),
        ("idx_repository", "mock/repository"),
        ("idx_tag_name", "v1.0.0"),
        ("idx_author", []),
        ("idx_project", ""),
        ("idx_published_at", None),
    ],
)
def test_release_index(attr, expected):
    mock_instance = MockModel()
    if attr == "idx_author" and not expected:
        mock_instance.author = None
    elif attr == "idx_project" and expected == "":
        mock_instance.repository.project = None
    elif attr == "idx_published_at" and expected is None:
        mock_instance.published_at = None
    assert getattr(mock_instance, attr) == expected
