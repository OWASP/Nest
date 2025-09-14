import pytest

from apps.api.rest.v0.sponsor import SponsorSchema


class TestSponsorSchema:
    @pytest.mark.parametrize(
        "sponsor_data",
        [
            {
                "name": "Gold Sponsor Inc.",
                "description": "A top-tier gold sponsor.",
                "url": "https://goldsponsor.com",
                "job_url": "https://goldsponsor.com/jobs",
                "image_url": "https://cdn.com/gold.png",
                "sponsor_type": "GOLD",
                "member_type": "PLATINUM",
                "is_member": True,
            },
            {
                "name": "Silver Sponsor LLC",
                "description": "A reliable silver sponsor.",
                "url": "https://silversponsor.com",
                "job_url": "",
                "image_url": "https://cdn.com/silver.png",
                "sponsor_type": "SILVER",
                "member_type": "SILVER",
                "is_member": True,
            },
        ],
    )
    def test_sponsor_schema_creation(self, sponsor_data):
        schema_instance = SponsorSchema(**sponsor_data)
        assert schema_instance.name == sponsor_data["name"]
        assert schema_instance.description == sponsor_data["description"]
        assert schema_instance.url == sponsor_data["url"]
        assert schema_instance.job_url == sponsor_data["job_url"]
        assert schema_instance.image_url == sponsor_data["image_url"]
        assert schema_instance.sponsor_type == sponsor_data["sponsor_type"]
        assert schema_instance.member_type == sponsor_data["member_type"]
        assert schema_instance.is_member == sponsor_data["is_member"]
