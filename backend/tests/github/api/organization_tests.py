from unittest.mock import MagicMock, patch

import pytest

from apps.github.api.organization import OrganizationSerializer
from apps.github.models.organization import Organization

class TestOrganizationSerializer:
    @pytest.mark.parametrize(
        "organization_data",
        [
            {
                "name": "GitHub",
                "login": "github",
                "company": "GitHub, Inc.",
                "location": "San Francisco, CA",
                "created_at": "2024-12-30T00:00:00Z",
                "updated_at": "2024-12-30T00:00:00Z",
            },
            {
                "name": "Microsoft",
                "login": "microsoft",
                "company": "Microsoft Corporation",
                "location": "Redmond, WA",
                "created_at": "2024-12-29T00:00:00Z",
                "updated_at": "2024-12-30T00:00:00Z",
            },
        ],
    )
    # Ensures that test runs without actual database access by simulating behavior of a queryset.
    @patch("apps.github.models.organization.Organization.objects.filter")
    def test_organization_serializer(self, mock_filter, organization_data):
        mock_qs = MagicMock()
        # To mimic a queryset where no matching objects are found.
        mock_qs.exists.return_value = False
        mock_filter.return_value = mock_qs

        serializer = OrganizationSerializer(data=organization_data)
        assert serializer.is_valid()
        validated_data = serializer.validated_data
        validated_data["created_at"] = (
            validated_data["created_at"].isoformat().replace("+00:00", "Z")
        )
        validated_data["updated_at"] = (
            validated_data["updated_at"].isoformat().replace("+00:00", "Z")
        )
        assert validated_data == organization_data

    @patch("apps.github.models.organization.Organization.objects.values_list")
    def test_get_logins(self, mock_values_list):
        mock_values_list.return_value = ["github", "microsoft"]
        logins = Organization.get_logins()
        assert logins == ["github", "microsoft"]
        mock_values_list.assert_called_once_with("name", flat=True)