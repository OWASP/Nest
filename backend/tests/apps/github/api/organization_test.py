from datetime import datetime

import pytest

from apps.github.api.organization import OrganizationSchema


class TestOrganizationSchema:
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
    def test_organization_schema(self, organization_data):
        schema = OrganizationSchema(**organization_data)
        assert schema.created_at == datetime.fromisoformat(organization_data["created_at"])
        assert schema.updated_at == datetime.fromisoformat(organization_data["updated_at"])

        assert schema.name == organization_data["name"]
        assert schema.login == organization_data["login"]
        assert schema.company == organization_data["company"]
        assert schema.location == organization_data["location"]
