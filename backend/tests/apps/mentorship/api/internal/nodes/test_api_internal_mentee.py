"""Pytest for mentorship mentee nodes."""

import pytest

from apps.mentorship.api.internal.nodes.enum import ExperienceLevelEnum
from apps.mentorship.api.internal.nodes.mentee import MenteeNode


@pytest.fixture
def mock_mentee_node():
    """Fixture for a mock MenteeNode instance."""
    mentee_node = MenteeNode(
        id="1",
        login="test_mentee",
        name="Test Mentee",
        avatar_url="https://example.com/avatar.jpg",
        bio="A test mentee",
        experience_level=ExperienceLevelEnum.BEGINNER,
        domains=["python"],
        tags=["backend"],
    )
    return mentee_node


def test_mentee_node_fields(mock_mentee_node):
    """Test that MenteeNode fields are correctly assigned."""
    assert mock_mentee_node.id == "1"
    assert mock_mentee_node.login == "test_mentee"
    assert mock_mentee_node.name == "Test Mentee"
    assert mock_mentee_node.avatar_url == "https://example.com/avatar.jpg"
    assert mock_mentee_node.bio == "A test mentee"
    assert mock_mentee_node.experience_level == ExperienceLevelEnum.BEGINNER
    assert mock_mentee_node.domains == ["python"]
    assert mock_mentee_node.tags == ["backend"]


def test_mentee_node_resolve_avatar_url(mock_mentee_node):
    """Test the resolve_avatar_url method."""
    assert mock_mentee_node.resolve_avatar_url() == "https://example.com/avatar.jpg"


def test_mentee_node_resolve_experience_level(mock_mentee_node):
    """Test the resolve_experience_level method."""
    assert mock_mentee_node.resolve_experience_level() == ExperienceLevelEnum.BEGINNER


def test_mentee_node_resolve_experience_level_none():
    """Test the resolve_experience_level method when experience_level is None."""
    mentee_node_no_exp = MenteeNode(
        id="2",
        login="no_exp_mentee",
        name="No Experience Mentee",
        avatar_url="https://example.com/noexp.jpg",
        bio=None,
        experience_level=None,  # type: ignore[assignment]
        domains=None,
        tags=None,
    )
    assert mentee_node_no_exp.resolve_experience_level() == "beginner"
