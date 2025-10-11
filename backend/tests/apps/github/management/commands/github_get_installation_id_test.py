"""Tests for the GitHub get installation ID management command."""

import os
from unittest import mock

import pytest
from django.test import SimpleTestCase


class TestGitHubGetInstallationId(SimpleTestCase):
    """Test the GitHub get installation ID management command."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_private_key = (
            "-----BEGIN FAKE TEST KEY-----\n"
            "This is a fake test key for testing purposes only\n"
            "-----END FAKE TEST KEY-----"
        )

    @mock.patch("apps.github.management.commands.github_get_installation_id.GithubIntegration")
    @mock.patch("apps.github.management.commands.github_get_installation_id.Auth.AppAuth")
    def test_get_installation_id_success(self, mock_app_auth, mock_github_integration):
        """Test successful retrieval of installation ID."""
        from apps.github.management.commands.github_get_installation_id import Command

        # Mock the installation
        mock_installation = mock.MagicMock()
        mock_installation.id = 12345
        mock_installation.account.type = "Organization"
        mock_installation.account.login = "test-org"

        # Mock the GithubIntegration
        mock_gi_instance = mock.MagicMock()
        mock_gi_instance.get_installations.return_value = [mock_installation]
        mock_github_integration.return_value = mock_gi_instance

        # Mock the AppAuth
        mock_auth_instance = mock.MagicMock()
        mock_app_auth.return_value = mock_auth_instance

        command = Command()
        with (
            mock.patch("pathlib.Path.open", mock.mock_open(read_data=self.test_private_key)),
            mock.patch("pathlib.Path.exists", return_value=True),
        ):
            command.handle(app_id=123456)

        # Verify the mocks were called correctly
        _, kwargs = mock_app_auth.call_args
        assert kwargs["app_id"] == 123456
        assert isinstance(kwargs["private_key"], str)
        mock_github_integration.assert_called_once_with(auth=mock_auth_instance)
        mock_gi_instance.get_installations.assert_called_once()

    @mock.patch("apps.github.management.commands.github_get_installation_id.GithubIntegration")
    @mock.patch("apps.github.management.commands.github_get_installation_id.Auth.AppAuth")
    def test_get_installation_id_no_installations(self, mock_app_auth, mock_github_integration):
        """Test when no installations are found."""
        from apps.github.management.commands.github_get_installation_id import Command

        # Mock empty installations
        mock_gi_instance = mock.MagicMock()
        mock_gi_instance.get_installations.return_value = []
        mock_github_integration.return_value = mock_gi_instance

        mock_auth_instance = mock.MagicMock()
        mock_app_auth.return_value = mock_auth_instance

        command = Command()
        with (
            mock.patch("pathlib.Path.open", mock.mock_open(read_data=self.test_private_key)),
            mock.patch("pathlib.Path.exists", return_value=True),
        ):
            command.handle(app_id=123456)

        mock_gi_instance.get_installations.assert_called_once()

    def test_get_installation_id_no_app_id(self):
        """Test when no app ID is provided."""
        from apps.github.management.commands.github_get_installation_id import Command

        command = Command()
        with pytest.raises(SystemExit):
            command.handle()

    def test_get_installation_id_private_key_file_not_found(self):
        """Test when private key file is not found."""
        from apps.github.management.commands.github_get_installation_id import Command

        command = Command()
        with (
            mock.patch("pathlib.Path.exists", return_value=False),
            pytest.raises(SystemExit),
        ):
            command.handle(app_id=123456)

    def test_get_installation_id_empty_private_key_file(self):
        """Test when private key file is empty."""
        from apps.github.management.commands.github_get_installation_id import Command

        command = Command()
        with (
            mock.patch("pathlib.Path.open", mock.mock_open(read_data="")),
            mock.patch("pathlib.Path.exists", return_value=True),
            pytest.raises(SystemExit),
        ):
            command.handle(app_id=123456)

    def test_get_installation_id_with_custom_private_key_file(self):
        """Test with custom private key file path."""
        from apps.github.management.commands.github_get_installation_id import Command

        custom_key_path = "/custom/path/key.pem"

        command = Command()
        with (
            mock.patch("pathlib.Path.open", mock.mock_open(read_data=self.test_private_key)),
            mock.patch("pathlib.Path.exists", return_value=True),
            mock.patch(
                "apps.github.management.commands.github_get_installation_id.GithubIntegration"
            ),
            mock.patch("apps.github.management.commands.github_get_installation_id.Auth.AppAuth"),
        ):
            command.handle(app_id=123456, private_key_file=custom_key_path)

    @mock.patch("apps.github.management.commands.github_get_installation_id.GithubIntegration")
    @mock.patch("apps.github.management.commands.github_get_installation_id.Auth.AppAuth")
    def test_get_installation_id_with_environment_app_id(
        self, mock_app_auth, mock_github_integration
    ):
        """Test using app ID from environment variable."""
        from apps.github.management.commands.github_get_installation_id import Command

        mock_gi_instance = mock.MagicMock()
        mock_gi_instance.get_installations.return_value = []
        mock_github_integration.return_value = mock_gi_instance

        mock_auth_instance = mock.MagicMock()
        mock_app_auth.return_value = mock_auth_instance

        command = Command()
        with (
            mock.patch.dict(os.environ, {"GITHUB_APP_ID": "123456"}),
            mock.patch("pathlib.Path.open", mock.mock_open(read_data=self.test_private_key)),
            mock.patch("pathlib.Path.exists", return_value=True),
        ):
            command.handle()

        _, kwargs = mock_app_auth.call_args
        assert kwargs["app_id"] == 123456
        assert isinstance(kwargs["private_key"], str)
