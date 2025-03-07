import pytest

from apps.github.models.organization import Organization


class TestOrganizationIndexMixin:
    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ("idx_name", "Organization Name login"),
            ("idx_company", "Company Location"),
        ],
    )
    def test_organization_index(self, attr, expected):
        organization = Organization(
            name="Organization Name",
            login="login",
            company="Company",
            location="Location",
        )
        assert getattr(organization, attr) == expected
