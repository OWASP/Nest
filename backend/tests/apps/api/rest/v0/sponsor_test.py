import pytest

from apps.api.rest.v0.sponsor import SponsorSchema


class TestSponsorSchema:
    @pytest.mark.parametrize(
        "sponsor_data",
        [
            {
                "description": "A top-tier gold sponsor.",
                "image_url": "https://cdn.com/gold.png",
                "is_member": True,
                "job_url": "https://goldsponsor.com/jobs",
                "key": "gold-sponsor-inc.",
                "member_type": "PLATINUM",
                "name": "Gold Sponsor Inc.",
                "sponsor_type": "GOLD",
                "url": "https://goldsponsor.com",
            },
            {
                "description": "A reliable silver sponsor.",
                "image_url": "https://cdn.com/silver.png",
                "is_member": True,
                "job_url": "",
                "key": "silver-sponsor-llc",
                "member_type": "SILVER",
                "name": "Silver Sponsor LLC",
                "sponsor_type": "SILVER",
                "url": "https://silversponsor.com",
            },
        ],
    )
    def test_sponsor_schema_creation(self, sponsor_data):
        """Test schema creation with valid data."""
        schema_instance = SponsorSchema(**sponsor_data)

        assert schema_instance.description == sponsor_data["description"]
        assert schema_instance.image_url == sponsor_data["image_url"]
        assert schema_instance.is_member == sponsor_data["is_member"]
        assert schema_instance.job_url == sponsor_data["job_url"]
        assert schema_instance.key == sponsor_data["key"]
        assert schema_instance.member_type == sponsor_data["member_type"]
        assert schema_instance.name == sponsor_data["name"]
        assert schema_instance.sponsor_type == sponsor_data["sponsor_type"]
        assert schema_instance.url == sponsor_data["url"]

    def test_sponsor_schema_with_minimal_data(self):
        """Test schema with minimal required fields."""
        minimal_data = {
            "description": "",
            "image_url": "",
            "is_member": False,
            "job_url": "",
            "key": "test-sponsor",
            "member_type": "",
            "name": "Test Sponsor",
            "sponsor_type": "SILVER",
            "url": "",
        }
        schema = SponsorSchema(**minimal_data)

        assert schema.job_url == ""
        assert schema.key == "test-sponsor"
        assert schema.name == "Test Sponsor"
