from datetime import datetime

import pytest

from apps.api.rest.v0.organization import OrganizationDetail


class TestOrganizationSchema:
    @pytest.mark.parametrize(
        "organization_data",
        [
            {
                "company": "GitHub, Inc.",
                "created_at": "2024-12-30T00:00:00Z",
                "location": "San Francisco, CA",
                "login": "github",
                "name": "GitHub",
                "updated_at": "2024-12-30T00:00:00Z",
            },
            {
                "company": "Microsoft Corporation",
                "created_at": "2024-12-29T00:00:00Z",
                "location": "Redmond, WA",
                "login": "microsoft",
                "name": "Microsoft",
                "updated_at": "2024-12-30T00:00:00Z",
            },
        ],
    )
    def test_organization_schema(self, organization_data):
        organization = OrganizationDetail(**organization_data)

        assert organization.company == organization_data["company"]
        assert organization.created_at == datetime.fromisoformat(organization_data["created_at"])
        assert organization.location == organization_data["location"]
        assert organization.login == organization_data["login"]
        assert organization.name == organization_data["name"]
        assert organization.updated_at == datetime.fromisoformat(organization_data["updated_at"])
