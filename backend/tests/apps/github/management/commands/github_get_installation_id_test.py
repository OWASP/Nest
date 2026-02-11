"""Tests for the GitHub get installation ID management command."""

import io
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

        with (
            mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout,
            mock.patch("pathlib.Path.open", mock.mock_open(read_data=self.test_private_key)),
            mock.patch("pathlib.Path.exists", return_value=True),
        ):
            command = Command()
            command.handle(app_id=123456)

        output = mock_stdout.getvalue()
        assert "Found 1 installation(s)" in output
        assert "Installation ID: 12345" in output
        assert "Account: test-org (Organization)" in output

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

        mock_gi_instance = mock.MagicMock()
        mock_gi_instance.get_installations.return_value = []
        mock_github_integration.return_value = mock_gi_instance

        mock_auth_instance = mock.MagicMock()
        mock_app_auth.return_value = mock_auth_instance

        with (
            mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout,
            mock.patch("pathlib.Path.open", mock.mock_open(read_data=self.test_private_key)),
            mock.patch("pathlib.Path.exists", return_value=True),
        ):
            command = Command()
            command.handle(app_id=123456)

        mock_gi_instance.get_installations.assert_called_once()
        assert "No installations found for GitHub App ID: 123456" in mock_stdout.getvalue()

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

    @mock.patch("apps.github.management.commands.github_get_installation_id.Path")
    def test_get_installation_id_with_custom_private_key_file(self, mock_path):
        """Test with custom private key file path."""
        from apps.github.management.commands.github_get_installation_id import Command

        custom_key_path = "/custom/path/key.pem"
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.open = mock.mock_open(read_data=self.test_private_key)

        command = Command()
        with (
            mock.patch(
                "apps.github.management.commands.github_get_installation_id.GithubIntegration"
            ),
            mock.patch("apps.github.management.commands.github_get_installation_id.Auth.AppAuth"),
        ):
            command.handle(app_id=123456, private_key_file=custom_key_path)

        mock_path.assert_any_call(custom_key_path)

    @mock.patch("apps.github.management.commands.github_get_installation_id.Auth.AppAuth")
    @mock.patch("apps.github.management.commands.github_get_installation_id.GithubIntegration")
    def test_get_installation_id_github_exception(self, mock_github_integration, mock_app_auth):
        """Test when a generic exception occurs during GitHub API interaction."""
        from apps.github.management.commands.github_get_installation_id import Command

        mock_app_auth.return_value = mock.MagicMock()
        mock_github_integration.side_effect = Exception("API Error")

        with (
            mock.patch("sys.stderr", new_callable=io.StringIO) as mock_stderr,
            mock.patch("pathlib.Path.open", mock.mock_open(read_data=self.test_private_key)),
            mock.patch("pathlib.Path.exists", return_value=True),
        ):
            command = Command()
            with pytest.raises(SystemExit):
                command.handle(app_id=123456)

        assert "Failed to get installations: API Error" in mock_stderr.getvalue()

    @mock.patch("apps.github.management.commands.github_get_installation_id.GithubIntegration")
    @mock.patch("apps.github.management.commands.github_get_installation_id.Auth.AppAuth")
    def test_get_installation_id_multiple_installations(
        self, mock_app_auth, mock_github_integration
    ):
        """Test successful retrieval of multiple installation IDs."""
        from apps.github.management.commands.github_get_installation_id import Command

        mock_installation_1 = mock.MagicMock()
        mock_installation_1.id = 12345
        mock_installation_1.account.type = "Organization"
        mock_installation_1.account.login = "test-org"

        mock_installation_2 = mock.MagicMock()
        mock_installation_2.id = 67890
        mock_installation_2.account.type = "User"
        mock_installation_2.account.login = "test-user"

        mock_gi_instance = mock.MagicMock()
        mock_gi_instance.get_installations.return_value = [
            mock_installation_1,
            mock_installation_2,
        ]
        mock_github_integration.return_value = mock_gi_instance

        mock_auth_instance = mock.MagicMock()
        mock_app_auth.return_value = mock_auth_instance

        with (
            mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout,
            mock.patch("pathlib.Path.open", mock.mock_open(read_data=self.test_private_key)),
            mock.patch("pathlib.Path.exists", return_value=True),
        ):
            command = Command()
            command.handle(app_id=123456)

        output = mock_stdout.getvalue()
        assert "Found 2 installation(s)" in output
        assert "Installation ID: 12345" in output
        assert "Account: test-org (Organization)" in output
        assert "Installation ID: 67890" in output
        assert "Account: test-user (User)" in output

    def test_get_installation_id_permission_error(self):
        """Test when a permission error occurs reading the private key file."""
        from apps.github.management.commands.github_get_installation_id import Command

        command = Command()
        with (
            mock.patch("pathlib.Path.open", side_effect=PermissionError),
            mock.patch("pathlib.Path.exists", return_value=True),
            pytest.raises(SystemExit),
        ):
            command.handle(app_id=123456)

    def test_get_installation_id_file_not_found_error(self):
        """Test when a file not found error occurs reading the private key file."""
        from apps.github.management.commands.github_get_installation_id import Command

        command = Command()
        with (
            mock.patch("pathlib.Path.open", side_effect=FileNotFoundError),
            mock.patch("pathlib.Path.exists", return_value=True),
            pytest.raises(SystemExit),
        ):
            command.handle(app_id=123456)

    def test_add_arguments(self):
        """Test that the command's arguments are correctly added."""
        from apps.github.management.commands.github_get_installation_id import Command

        mock_parser = mock.MagicMock()
        command = Command()
        command.add_arguments(mock_parser)

        mock_parser.add_argument.assert_any_call(
            "--app-id",
            type=int,
            help="GitHub App ID (overrides GITHUB_APP_ID environment variable)",
        )
        mock_parser.add_argument.assert_any_call(
            "--private-key-file",
            type=str,
            help="Path to private key file (overrides default backend/.github.pem)",
        )

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

    @mock.patch("apps.github.management.commands.github_get_installation_id.GithubIntegration")
    @mock.patch("apps.github.management.commands.github_get_installation_id.Auth.AppAuth")
    def test_get_installation_id_no_account(self, mock_app_auth, mock_github_integration):
        """Test installation without account attribute (branch 104->108)."""
        from apps.github.management.commands.github_get_installation_id import Command

        mock_installation = mock.MagicMock(spec=["id"])
        mock_installation.id = 99999

        mock_gi_instance = mock.MagicMock()
        mock_gi_instance.get_installations.return_value = [mock_installation]
        mock_github_integration.return_value = mock_gi_instance

        mock_auth_instance = mock.MagicMock()
        mock_app_auth.return_value = mock_auth_instance

        with (
            mock.patch("sys.stdout", new_callable=io.StringIO) as mock_stdout,
            mock.patch("pathlib.Path.open", mock.mock_open(read_data=self.test_private_key)),
            mock.patch("pathlib.Path.exists", return_value=True),
        ):
            command = Command()
            command.handle(app_id=123456)

        output = mock_stdout.getvalue()
        assert "Installation ID: 99999" in output
        assert "Account:" not in output
