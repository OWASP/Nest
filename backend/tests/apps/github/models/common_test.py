from unittest import mock

import pytest
from github.GithubException import UnknownObjectException

from apps.github.models.common import GenericUserModel, NodeModel


class TestGenericUserModel(GenericUserModel):
    """A concrete class for testing the abstract GenericUserModel."""

    __test__ = False

    class Meta:
        app_label = "github"


class TestGenericUserModelProperties:
    @pytest.fixture
    def user(self):
        return TestGenericUserModel(login="testuser", name="Test User")

    def test_nest_key(self, user):
        assert user.nest_key == "testuser"

    def test_title_with_name(self, user):
        assert user.title == "Test User (testuser)"

    def test_title_without_name(self):
        user = TestGenericUserModel(login="testuser", name="")
        assert user.title == "testuser"

    def test_title_with_same_name_and_login(self):
        user = TestGenericUserModel(login="testuser", name="testuser")
        assert user.title == "testuser"

    def test_url(self, user):
        assert user.url == "https://github.com/testuser"


class TestGenericUserModelFromGithub:
    def test_from_github(self):
        mock_data = mock.Mock()
        mock_data.avatar_url = "http://example.com/avatar.png"
        mock_data.collaborators = 10
        mock_data.company = "Test Inc."
        mock_data.created_at = "2023-01-01T00:00:00Z"
        mock_data.email = "test@example.com"
        mock_data.followers = 20
        mock_data.following = 30
        mock_data.location = "Test Location"
        mock_data.login = "testuser"
        mock_data.name = "Test User"
        mock_data.public_gists = 5
        mock_data.public_repos = 15
        mock_data.updated_at = "2023-01-01T00:00:00Z"

        user = TestGenericUserModel()
        user.from_github(mock_data)

        assert user.avatar_url == "http://example.com/avatar.png"
        assert user.collaborators_count == 10
        assert user.company == "Test Inc."
        assert user.created_at == "2023-01-01T00:00:00Z"
        assert user.email == "test@example.com"
        assert user.followers_count == 20
        assert user.following_count == 30
        assert user.location == "Test Location"
        assert user.login == "testuser"
        assert user.name == "Test User"
        assert user.public_gists_count == 5
        assert user.public_repositories_count == 15
        assert user.updated_at == "2023-01-01T00:00:00Z"

    def test_from_github_with_missing_data(self):
        mock_data = mock.Mock()
        mock_data.login = "testuser"
        mock_data.created_at = "2023-01-01T00:00:00Z"
        mock_data.updated_at = "2023-01-01T00:00:00Z"
        mock_data.avatar_url = None
        mock_data.collaborators = None
        mock_data.company = None
        mock_data.email = None
        mock_data.followers = None
        mock_data.following = None
        mock_data.location = None
        mock_data.name = None
        mock_data.public_gists = None
        mock_data.public_repos = None

        user = TestGenericUserModel()
        user.from_github(mock_data)

        assert user.login == "testuser"
        assert user.name == ""
        assert user.email == ""


class TestNodeModel(NodeModel):
    """A concrete class for testing the abstract NodeModel."""

    __test__ = False

    class Meta:
        app_label = "github"


class TestNodeModelMethods:
    def test_get_node_id(self):
        mock_node = mock.Mock()
        mock_node.raw_data = {"node_id": "test_node_id"}
        assert TestNodeModel.get_node_id(mock_node) == "test_node_id"

    def test_get_node_id_raises_exception(self):
        mock_node = mock.Mock()
        mock_node.raw_data = {}
        type(mock_node).raw_data = mock.PropertyMock(
            side_effect=UnknownObjectException(404, "Not Found")
        )
        assert TestNodeModel.get_node_id(mock_node) is None
