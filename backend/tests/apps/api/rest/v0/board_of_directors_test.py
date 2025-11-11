from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from apps.api.rest.v0.board_of_directors import (
    BoardOfDirectorsSchema,
    EntityMemberSchema,
)


class TestBoardOfDirectorsSchema:
    """Test BoardOfDirectors schema."""

    @pytest.mark.parametrize(
        "board_data",
        [
            {
                "year": 2024,
                "created_at": "2024-12-30T00:00:00Z",
                "updated_at": "2024-12-30T00:00:00Z",
                "members": [
                    {
                        "member_name": "Alice",
                        "member_email": "alice@example.com",
                        "role": "member",
                        "order": 100,
                        "is_active": True,
                        "is_reviewed": True,
                    }
                ],
                "candidates": [],
            },
            {
                "year": 2025,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-15T00:00:00Z",
                "members": [],
                "candidates": [
                    {
                        "member_name": "Bob",
                        "member_email": "bob@example.com",
                        "role": "candidate",
                        "order": 1,
                        "is_active": True,
                        "is_reviewed": False,
                    }
                ],
            },
        ],
    )
    def test_board_schema_valid(self, board_data):
        """Test that BoardOfDirectorsSchema correctly parses valid board data."""
        schema = BoardOfDirectorsSchema(**board_data)
        assert schema.created_at == datetime.fromisoformat(board_data["created_at"])
        assert schema.updated_at == datetime.fromisoformat(board_data["updated_at"])
        assert schema.year == board_data["year"]
        assert isinstance(schema.members, list)
        assert isinstance(schema.candidates, list)
        assert len(schema.members) == len(board_data["members"])
        assert len(schema.candidates) == len(board_data["candidates"])

    def test_board_schema_with_multiple_members_and_candidates(self):
        """Test board with multiple members and candidates."""
        board_data = {
            "year": 2025,
            "created_at": datetime(2025, 1, 1, tzinfo=UTC),
            "updated_at": datetime(2025, 1, 15, tzinfo=UTC),
            "members": [
                {
                    "member_name": "John Doe",
                    "member_email": "john@example.com",
                    "role": "member",
                    "order": 1,
                    "is_active": True,
                    "is_reviewed": True,
                },
                {
                    "member_name": "Jane Smith",
                    "member_email": "jane@example.com",
                    "role": "member",
                    "order": 2,
                    "is_active": True,
                    "is_reviewed": True,
                },
            ],
            "candidates": [
                {
                    "member_name": "Bob Wilson",
                    "member_email": "bob@example.com",
                    "role": "candidate",
                    "order": 1,
                    "is_active": True,
                    "is_reviewed": False,
                },
                {
                    "member_name": "Alice Brown",
                    "member_email": "alice@example.com",
                    "role": "candidate",
                    "order": 2,
                    "is_active": False,
                    "is_reviewed": False,
                },
            ],
        }

        schema = BoardOfDirectorsSchema(**board_data)

        assert schema.year == 2025
        assert len(schema.members) == 2
        assert len(schema.candidates) == 2
        assert schema.members[0].member_name == "John Doe"
        assert schema.members[1].member_name == "Jane Smith"
        assert schema.candidates[0].is_active is True
        assert schema.candidates[1].is_active is False

    def test_board_schema_missing_year_fails(self):
        """Test that missing year field fails validation."""
        board_data = {
            "created_at": "2024-12-30T00:00:00Z",
            "updated_at": "2024-12-30T00:00:00Z",
            "members": [],
            "candidates": [],
        }

        with pytest.raises(ValidationError) as exc_info:
            BoardOfDirectorsSchema(**board_data)

        assert "year" in str(exc_info.value)

    def test_board_schema_missing_created_at_fails(self):
        """Test that missing created_at field fails validation."""
        board_data = {
            "year": 2024,
            "updated_at": "2024-12-30T00:00:00Z",
            "members": [],
            "candidates": [],
        }

        with pytest.raises(ValidationError) as exc_info:
            BoardOfDirectorsSchema(**board_data)

        assert "created_at" in str(exc_info.value)

    def test_board_schema_invalid_year_type_fails(self):
        """Test that invalid year type fails validation."""
        board_data = {
            "year": "invalid",
            "created_at": "2024-12-30T00:00:00Z",
            "updated_at": "2024-12-30T00:00:00Z",
            "members": [],
            "candidates": [],
        }

        with pytest.raises(ValidationError) as exc_info:
            BoardOfDirectorsSchema(**board_data)

        assert "year" in str(exc_info.value)

    def test_board_schema_invalid_datetime_format_fails(self):
        """Test that invalid datetime format fails validation."""
        board_data = {
            "year": 2024,
            "created_at": "invalid-date",
            "updated_at": "2024-12-30T00:00:00Z",
            "members": [],
            "candidates": [],
        }

        with pytest.raises(ValidationError) as exc_info:
            BoardOfDirectorsSchema(**board_data)

        assert "created_at" in str(exc_info.value)

    def test_board_schema_missing_members_list_fails(self):
        """Test that missing members list fails validation."""
        board_data = {
            "year": 2024,
            "created_at": "2024-12-30T00:00:00Z",
            "updated_at": "2024-12-30T00:00:00Z",
            "candidates": [],
        }

        with pytest.raises(ValidationError) as exc_info:
            BoardOfDirectorsSchema(**board_data)

        assert "members" in str(exc_info.value)


class TestEntityMemberSchema:
    """Test EntityMember schema."""

    def test_entity_member_schema_valid(self):
        """Test that EntityMemberSchema correctly parses valid member data."""
        member_data = {
            "member_name": "Test Member",
            "member_email": "test@example.com",
            "role": "member",
            "order": 1,
            "is_active": True,
            "is_reviewed": True,
        }

        schema = EntityMemberSchema(**member_data)

        assert schema.member_name == "Test Member"
        assert schema.member_email == "test@example.com"
        assert schema.role == "member"
        assert schema.order == 1
        assert schema.is_active is True
        assert schema.is_reviewed is True

    def test_entity_member_schema_candidate(self):
        """Test EntityMemberSchema with candidate role."""
        member_data = {
            "member_name": "Jane Candidate",
            "member_email": "jane@example.com",
            "role": "candidate",
            "order": 5,
            "is_active": False,
            "is_reviewed": False,
        }

        schema = EntityMemberSchema(**member_data)

        assert schema.role == "candidate"
        assert schema.is_active is False
        assert schema.is_reviewed is False

    def test_entity_member_schema_missing_name_fails(self):
        """Test that missing member_name fails validation."""
        member_data = {
            "member_email": "test@example.com",
            "role": "member",
            "order": 1,
            "is_active": True,
            "is_reviewed": True,
        }

        with pytest.raises(ValidationError) as exc_info:
            EntityMemberSchema(**member_data)

        assert "member_name" in str(exc_info.value)

    def test_entity_member_schema_missing_email_fails(self):
        """Test that missing member_email fails validation."""
        member_data = {
            "member_name": "Test Member",
            "role": "member",
            "order": 1,
            "is_active": True,
            "is_reviewed": True,
        }

        with pytest.raises(ValidationError) as exc_info:
            EntityMemberSchema(**member_data)

        assert "member_email" in str(exc_info.value)

    def test_entity_member_schema_missing_role_fails(self):
        """Test that missing role fails validation."""
        member_data = {
            "member_name": "Test Member",
            "member_email": "test@example.com",
            "order": 1,
            "is_active": True,
            "is_reviewed": True,
        }

        with pytest.raises(ValidationError) as exc_info:
            EntityMemberSchema(**member_data)

        assert "role" in str(exc_info.value)

    def test_entity_member_schema_invalid_order_type_fails(self):
        """Test that invalid order type fails validation."""
        member_data = {
            "member_name": "Test Member",
            "member_email": "test@example.com",
            "role": "member",
            "order": "invalid",
            "is_active": True,
            "is_reviewed": True,
        }

        with pytest.raises(ValidationError) as exc_info:
            EntityMemberSchema(**member_data)

        assert "order" in str(exc_info.value)

    def test_entity_member_schema_invalid_is_active_type_fails(self):
        """Test that invalid is_active type fails validation."""
        member_data = {
            "member_name": "Test Member",
            "member_email": "test@example.com",
            "role": "member",
            "order": 1,
            "is_active": "yes",
            "is_reviewed": True,
        }

        with pytest.raises(ValidationError) as exc_info:
            EntityMemberSchema(**member_data)

        assert "is_active" in str(exc_info.value)
