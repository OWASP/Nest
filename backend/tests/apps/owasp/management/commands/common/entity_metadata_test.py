import io
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command

from apps.owasp.management.commands.common.entity_metadata import EntityMetadataBase


class ConcreteTestCommand(EntityMetadataBase):
    model = MagicMock()
    get_metadata = MagicMock()


class TestEntityMetadataBase:
    """Test suite for the EntityMetadataBase command's core functionality."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Reset mocks before each test to ensure test isolation."""
        ConcreteTestCommand.model = MagicMock()
        ConcreteTestCommand.model.__name__ = "TestModel"
        ConcreteTestCommand.get_metadata.reset_mock()

    @patch("apps.owasp.management.commands.common.entity_metadata.Path")
    @patch(
        "apps.owasp.management.commands.common.entity_metadata.validate_data", return_value=None
    )
    @patch("apps.owasp.management.commands.common.entity_metadata.get_schema")
    @patch("apps.owasp.management.commands.common.entity_metadata.yaml.dump")
    def test_handle_success(self, mock_yaml_dump, mock_get_schema, mock_validate, mock_path):
        """Test successful execution of the handle method."""
        mock_dir_instance = mock_path.return_value
        mock_file_instance = mock_dir_instance.__truediv__.return_value
        mock_file_instance.open.return_value.__enter__.return_value = MagicMock()

        command_instance = ConcreteTestCommand()
        entity_instance = MagicMock()
        command_instance.model.objects.get.return_value = entity_instance
        metadata = {"name": "Test Name", "key": "test-key"}
        command_instance.get_metadata.return_value = metadata

        stdout = io.StringIO()

        call_command(command_instance, "test-key", stdout=stdout)

        command_instance.model.objects.get.assert_called_once_with(key="test-key")
        command_instance.get_metadata.assert_called_once_with(entity_instance)
        mock_get_schema.assert_called_once_with("testmodel")
        mock_validate.assert_called_once_with(schema=mock_get_schema.return_value, data=metadata)
        mock_path.assert_called_once_with("data/schema/testmodel")
        mock_dir_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_dir_instance.__truediv__.assert_called_once_with("test-key.owasp.yaml")
        mock_file_instance.open.assert_called_once_with("w")

        mock_yaml_dump.assert_called_once()
        assert "Successfully generated file" in stdout.getvalue()

    def test_handle_model_not_set(self):
        """Test handle method when model is not set."""
        command_instance = ConcreteTestCommand()
        command_instance.model = None
        stderr = io.StringIO()

        call_command(command_instance, "any-key", stderr=stderr)

        assert "OWASP entity model is not set" in stderr.getvalue()

    def test_handle_entity_not_found(self):
        """Test handle method when entity is not found."""
        command_instance = ConcreteTestCommand()
        model_class = command_instance.model
        model_class.DoesNotExist = Exception
        model_class.objects.get.side_effect = model_class.DoesNotExist

        stderr = io.StringIO()
        call_command(command_instance, "unknown-key", stderr=stderr)

        model_class.objects.get.assert_called_once_with(key="unknown-key")
        assert "TestModel with key 'unknown-key' not found" in stderr.getvalue()
