from unittest.mock import MagicMock, patch

import pytest

from apps.github.api.organization import OrganizationSerializer


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
@patch("apps.github.models.organization.Organization.objects.filter")
def test_organization_serializer(mock_filter, organization_data):
    mock_qs = MagicMock()
    mock_qs.exists.return_value = False
    mock_filter.return_value = mock_qs

    serializer = OrganizationSerializer(data=organization_data)
    assert serializer.is_valid()
    validated_data = serializer.validated_data
    validated_data["created_at"] = validated_data["created_at"].isoformat().replace("+00:00", "Z")
    validated_data["updated_at"] = validated_data["updated_at"].isoformat().replace("+00:00", "Z")
    assert validated_data == organization_data
