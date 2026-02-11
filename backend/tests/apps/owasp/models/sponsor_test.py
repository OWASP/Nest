"""Tests for Sponsor model."""

from unittest.mock import Mock, patch

import pytest

from apps.owasp.models.sponsor import Sponsor


class TestSponsorModel:
    """Tests for Sponsor model."""

    @patch("apps.owasp.models.sponsor.Sponsor.objects.get")
    def test_update_data_existing_sponsor(self, mock_get):
        """Test update_data updates existing sponsor."""
        mock_sponsor = Mock()
        mock_get.return_value = mock_sponsor
        data = {
            "name": "Test Sponsor",
            "description": "A test sponsor",
        }

        result = Sponsor.update_data(data)

        mock_get.assert_called_once()
        mock_sponsor.from_dict.assert_called_once_with(data)
        mock_sponsor.save.assert_called_once()
        assert result == mock_sponsor

    @patch("apps.owasp.models.sponsor.Sponsor.objects.get")
    def test_update_data_creates_new_sponsor(self, mock_get):
        """Test update_data creates new sponsor when it doesn't exist."""
        mock_get.side_effect = Sponsor.DoesNotExist
        data = {
            "name": "New Sponsor",
            "description": "A new sponsor",
        }

        with patch.object(Sponsor, "from_dict"), patch.object(Sponsor, "save"):
            result = Sponsor.update_data(data)

        mock_get.assert_called_once()
        assert isinstance(result, Sponsor)

    @patch("apps.owasp.models.sponsor.Sponsor.objects.get")
    def test_update_data_with_save_false(self, mock_get):
        """Test update_data with save=False doesn't call save."""
        mock_sponsor = Mock()
        mock_get.return_value = mock_sponsor
        data = {
            "name": "Test Sponsor",
            "description": "A test sponsor",
        }

        result = Sponsor.update_data(data, save=False)

        mock_get.assert_called_once()
        mock_sponsor.from_dict.assert_called_once_with(data)
        mock_sponsor.save.assert_not_called()
        assert result == mock_sponsor
