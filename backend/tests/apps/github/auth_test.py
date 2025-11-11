"""Tests for GitHub App authentication."""

import os
from pathlib import Path
from unittest import mock

import pytest
from github.GithubException import BadCredentialsException

from apps.github.auth import GitHubAppAuth, get_github_client


class TestGitHubAppAuth:
    """Test GitHub App authentication."""

    def test_init_with_app_config(self):
        """Test initialization with GitHub App configuration."""
        with (
            mock.patch("apps.github.auth.settings") as mock_settings,
            mock.patch.object(GitHubAppAuth, "_load_private_key", return_value="test-key"),
        ):
            mock_settings.GITHUB_APP_ID = "12345"
            mock_settings.GITHUB_APP_INSTALLATION_ID = "67890"
            auth = GitHubAppAuth()
            assert auth.app_id == "12345"
            assert auth.private_key == "test-key"
            assert auth.app_installation_id == "67890"
            assert auth._is_app_configured() is True

    def test_init_with_pat_fallback(self):
        """Test initialization with PAT fallback."""
        with (
            mock.patch("apps.github.auth.settings") as mock_settings,
            mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-pat"}),
        ):
            mock_settings.GITHUB_APP_ID = None
            mock_settings.GITHUB_APP_INSTALLATION_ID = None
            auth = GitHubAppAuth()
            assert auth.pat_token == "test-pat"  # noqa: S105
            assert auth._is_app_configured() is False

    def test_init_with_no_config(self):
        """Test initialization with no configuration."""
        with (
            mock.patch("apps.github.auth.settings") as mock_settings,
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch.object(GitHubAppAuth, "_load_private_key", return_value=None),
        ):
            mock_settings.GITHUB_APP_ID = None
            mock_settings.GITHUB_APP_INSTALLATION_ID = None
            with pytest.raises(ValueError, match="GitHub App configuration is incomplete"):
                GitHubAppAuth()

    @pytest.mark.parametrize(
        ("app_id", "private_key", "installation_id", "expected"),
        [
            ("1", "key", "1", True),
            (None, "key", "1", False),
            ("1", None, "1", False),
            ("1", "key", None, False),
            (None, None, "1", False),
            ("1", None, None, False),
            (None, "key", None, False),
            (None, None, None, False),
        ],
    )
    def test_is_app_configured(self, app_id, private_key, installation_id, expected):
        """Test the _is_app_configured method with various inputs."""
        with mock.patch("apps.github.auth.settings") as mock_settings:
            mock_settings.GITHUB_APP_ID = app_id
            mock_settings.GITHUB_APP_INSTALLATION_ID = installation_id
            with mock.patch.object(GitHubAppAuth, "_load_private_key", return_value=private_key):
                auth = GitHubAppAuth()
                assert auth._is_app_configured() is expected

    def test_load_private_key_success(self):
        """Test successful private key loading from file."""
        with (
            mock.patch.object(Path, "exists", return_value=True),
            mock.patch.object(Path, "open", mock.mock_open(read_data="test-private-key")),
            mock.patch("apps.github.auth.settings") as mock_settings,
        ):
            mock_settings.BASE_DIR = "/test/path"
            mock_settings.GITHUB_APP_ID = None
            mock_settings.GITHUB_APP_INSTALLATION_ID = None
            auth = GitHubAppAuth()
            private_key = auth._load_private_key()
            assert private_key == "test-private-key"

    def test_load_private_key_file_not_found(self):
        """Test private key loading when file doesn't exist."""
        with (
            mock.patch.object(Path, "exists", return_value=False),
            mock.patch("apps.github.auth.settings") as mock_settings,
        ):
            mock_settings.BASE_DIR = "/test/path"
            mock_settings.GITHUB_APP_ID = None
            mock_settings.GITHUB_APP_INSTALLATION_ID = None
            auth = GitHubAppAuth()
            private_key = auth._load_private_key()
            assert private_key is None

    def test_load_private_key_empty_file(self):
        """Test private key loading from empty file."""
        m = mock.mock_open(read_data="")
        with (
            mock.patch.object(Path, "exists", return_value=True),
            mock.patch.object(Path, "open", m),
            mock.patch("apps.github.auth.settings") as mock_settings,
        ):
            mock_settings.BASE_DIR = "/test/path"
            mock_settings.GITHUB_APP_ID = None
            mock_settings.GITHUB_APP_INSTALLATION_ID = None
            auth = GitHubAppAuth()
            private_key = auth._load_private_key()
            assert private_key == ""

    def test_load_private_key_file_error(self):
        """Test private key loading with file read error."""
        with (
            mock.patch.object(Path, "exists", return_value=True),
            mock.patch.object(Path, "open", side_effect=PermissionError("Access denied")),
            mock.patch("apps.github.auth.settings") as mock_settings,
        ):
            mock_settings.BASE_DIR = "/test/path"
            mock_settings.GITHUB_APP_ID = None
            mock_settings.GITHUB_APP_INSTALLATION_ID = None
            auth = GitHubAppAuth()
            private_key = auth._load_private_key()
            assert private_key is None

    def test_get_github_client_with_app_auth(self):
        """Test GitHub client creation with PyGithub App authentication."""
        with (
            mock.patch("apps.github.auth.settings") as mock_settings,
            mock.patch.object(GitHubAppAuth, "_load_private_key", return_value="test-key"),
        ):
            mock_settings.GITHUB_APP_ID = "12345"
            mock_settings.GITHUB_APP_INSTALLATION_ID = "67890"
            auth = GitHubAppAuth()
            with (
                mock.patch("apps.github.auth.Auth.AppAuth") as mock_app_auth,
                mock.patch("apps.github.auth.Auth.AppInstallationAuth") as mock_installation_auth,
                mock.patch("apps.github.auth.Github") as mock_github,
            ):
                mock_app_auth_instance = mock.Mock()
                mock_app_auth.return_value = mock_app_auth_instance

                mock_installation_auth_instance = mock.Mock()
                mock_installation_auth.return_value = mock_installation_auth_instance

                mock_client = mock.Mock()
                mock_github.return_value = mock_client

                client = auth.get_github_client()

                mock_app_auth.assert_called_once_with(
                    app_id="12345",
                    private_key="test-key",
                )
                mock_installation_auth.assert_called_once_with(
                    app_auth=mock_app_auth_instance,
                    installation_id=67890,
                )
                mock_github.assert_called_once_with(
                    auth=mock_installation_auth_instance,
                    per_page=100,
                )
                assert client == mock_client

    def test_get_github_client_with_pat_fallback(self):
        """Test GitHub client creation with PAT fallback."""
        with (
            mock.patch("apps.github.auth.settings") as mock_settings,
            mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-pat"}),
            mock.patch("apps.github.auth.Github") as mock_github,
        ):
            mock_settings.GITHUB_APP_ID = None
            mock_settings.GITHUB_APP_INSTALLATION_ID = None
            auth = GitHubAppAuth()
            mock_client = mock.Mock()
            mock_github.return_value = mock_client
            client = auth.get_github_client()
            mock_github.assert_called_once_with("test-pat", per_page=100)
            assert client == mock_client

    def test_get_github_client_with_custom_per_page(self):
        """Test GitHub client creation with custom per_page parameter."""
        with (
            mock.patch("apps.github.auth.settings") as mock_settings,
            mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-pat"}),
            mock.patch("apps.github.auth.Github") as mock_github,
        ):
            mock_settings.GITHUB_APP_ID = None
            mock_settings.GITHUB_APP_INSTALLATION_ID = None
            auth = GitHubAppAuth()
            mock_client = mock.Mock()
            mock_github.return_value = mock_client
            client = auth.get_github_client(per_page=50)
            mock_github.assert_called_once_with("test-pat", per_page=50)
            assert client == mock_client

    def test_get_github_client_authentication_error(self):
        """Test GitHub client creation with authentication error."""
        with (
            mock.patch("apps.github.auth.settings") as mock_settings,
            mock.patch.dict(os.environ, {"GITHUB_TOKEN": "invalid-token"}),
            mock.patch("apps.github.auth.Github") as mock_github,
        ):
            mock_settings.GITHUB_APP_ID = None
            mock_settings.GITHUB_APP_INSTALLATION_ID = None
            auth = GitHubAppAuth()
            mock_github.side_effect = BadCredentialsException(401, "Invalid token", None)
            with pytest.raises(BadCredentialsException):
                auth.get_github_client()


class TestGetGitHubClient:
    """Test the get_github_client function."""

    def test_get_github_client_function(self):
        """Test the get_github_client function."""
        with (
            mock.patch("apps.github.auth.settings") as mock_settings,
            mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-pat"}),
            mock.patch("apps.github.auth.Github") as mock_github,
        ):
            mock_settings.GITHUB_APP_ID = None
            mock_settings.GITHUB_APP_INSTALLATION_ID = None
            mock_client = mock.Mock()
            mock_github.return_value = mock_client
            client = get_github_client()
            assert client == mock_client
