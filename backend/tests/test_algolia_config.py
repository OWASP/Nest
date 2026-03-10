"""Tests for Algolia configuration validation."""
from django.test import TestCase, override_settings
from apps.common.validators.algolia_validator import (
    validate_algolia_config,
    AlgoliaConfigError,
    is_algolia_configured,
)


class TestAlgoliaConfiguration(TestCase):
    """Test Algolia configuration validation."""

    @override_settings(
        ALGOLIA_APPLICATION_ID="test-app-id",
        ALGOLIA_WRITE_API_KEY="test-api-key",
    )
    def test_validate_algolia_config_with_valid_config(self):
        """Test validation passes with valid configuration."""
        config = validate_algolia_config()
        self.assertEqual(config["app_id"], "test-app-id")
        self.assertEqual(config["api_key"], "test-api-key")

    @override_settings(ALGOLIA_WRITE_API_KEY="test-key")
    def test_validate_algolia_config_missing_app_id(self):
        """Test validation fails when APP_ID is missing."""
        with self.assertRaises(AlgoliaConfigError):
            validate_algolia_config()

    @override_settings(ALGOLIA_APPLICATION_ID="test-id")
    def test_validate_algolia_config_missing_api_key(self):
        """Test validation fails when API_KEY is missing."""
        with self.assertRaises(AlgoliaConfigError):
            validate_algolia_config()

    def test_is_algolia_configured_returns_false_when_invalid(self):
        """Test is_algolia_configured returns False with invalid config."""
        self.assertFalse(is_algolia_configured())
