"""Pytest for mentorship mentor nodes."""

from unittest.mock import MagicMock

import pytest

from apps.mentorship.api.internal.nodes.mentor import MentorNode


@pytest.fixture
def mock_github_user():
    """Fixture for a mock GithubUser."""
    mock = MagicMock()
    mock.avatar_url = "https://example.com/mentor_avatar.jpg"
    mock.name = "Mentor Name"
    mock.login = "mentorlogin"
    return mock


@pytest.fixture
def mock_mentor_node(mock_github_user):
    """Fixture for a mock MentorNode instance."""
    mentor_node = MentorNode(id="1")
    mentor_node.github_user = mock_github_user
    return mentor_node


@pytest.fixture
def mock_mentor_node_no_github_user():
    """Fixture for a mock MentorNode instance without a GitHub user."""
    mentor_node = MentorNode(id="2")
    mentor_node.github_user = None
    return mentor_node


def test_mentor_node_id(mock_mentor_node):
    """Test that MentorNode id is correctly assigned."""
    assert str(mock_mentor_node.id) == "1"


def test_mentor_node_avatar_url(mock_mentor_node):
    """Test the avatar_url field resolver."""
    assert mock_mentor_node.avatar_url() == "https://example.com/mentor_avatar.jpg"


def test_mentor_node_avatar_url_no_github_user(mock_mentor_node_no_github_user):
    """Test avatar_url when no github_user is associated."""
    assert mock_mentor_node_no_github_user.avatar_url() == ""


def test_mentor_node_name(mock_mentor_node):
    """Test the name field resolver."""
    assert mock_mentor_node.name() == "Mentor Name"


def test_mentor_node_name_no_github_user(mock_mentor_node_no_github_user):
    """Test name when no github_user is associated."""
    assert mock_mentor_node_no_github_user.name() == ""


def test_mentor_node_login(mock_mentor_node):
    """Test the login field resolver."""
    assert mock_mentor_node.login() == "mentorlogin"


def test_mentor_node_login_no_github_user(mock_mentor_node_no_github_user):
    """Test login when no github_user is associated."""
    assert mock_mentor_node_no_github_user.login() == ""