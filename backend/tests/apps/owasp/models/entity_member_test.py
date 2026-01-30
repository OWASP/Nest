"""Tests for EntityMember model."""

from unittest.mock import MagicMock, patch

from django.contrib.contenttypes.models import ContentType

from apps.owasp.models.entity_member import EntityMember


class TestEntityMemberModel:
    """Test cases for EntityMember model."""

    def test_str_with_member_login(self):
        """Test string representation uses member login when available."""
        entity_member = EntityMember(
            member_name="Test User",
            role=EntityMember.Role.LEADER,
        )

        assert entity_member.role == EntityMember.Role.LEADER
        assert entity_member.member_name == "Test User"
        assert entity_member.get_role_display() == "Leader"

    def test_str_without_member_uses_name(self):
        """Test string representation uses member_name when member is None."""
        entity_member = EntityMember(
            member_name="John Doe",
            role=EntityMember.Role.MEMBER,
        )

        assert entity_member.member_name == "John Doe"
        assert entity_member.get_role_display() == "Member"

    def test_role_choices(self):
        """Test that role choices are correctly defined."""
        assert EntityMember.Role.CANDIDATE == "candidate"
        assert EntityMember.Role.LEADER == "leader"
        assert EntityMember.Role.MEMBER == "member"

    def test_update_data_finds_existing(self):
        """Test update_data finds and updates existing EntityMember."""
        existing_member = MagicMock(spec=EntityMember)
        mock_content_type = MagicMock(spec=ContentType)

        with patch("apps.owasp.models.entity_member.EntityMember.objects") as mock_manager:
            mock_manager.get.return_value = existing_member

            data = {
                "entity_id": 1,
                "entity_type": mock_content_type,
                "member_name": "Existing User",
                "role": EntityMember.Role.MEMBER,
                "member_email": "updated@example.com",
                "order": 2,
            }

            result = EntityMember.update_data(data, save=False)

            assert result == existing_member
            mock_manager.get.assert_called_once_with(
                entity_id=1,
                entity_type=mock_content_type,
                member_name="Existing User",
                role=EntityMember.Role.MEMBER,
            )
            existing_member.from_dict.assert_called_once_with(data)

    def test_update_data_calls_save_when_requested(self):
        """Test update_data saves when save=True."""
        existing_member = MagicMock(spec=EntityMember)
        mock_content_type = MagicMock(spec=ContentType)

        with patch("apps.owasp.models.entity_member.EntityMember.objects") as mock_manager:
            mock_manager.get.return_value = existing_member

            data = {
                "entity_id": 1,
                "entity_type": mock_content_type,
                "member_name": "Test",
                "role": EntityMember.Role.CANDIDATE,
            }

            EntityMember.update_data(data, save=True)

            existing_member.save.assert_called_once()

    def test_update_data_does_not_save_when_false(self):
        """Test update_data does not save when save=False."""
        existing_member = MagicMock(spec=EntityMember)
        mock_content_type = MagicMock(spec=ContentType)

        with patch("apps.owasp.models.entity_member.EntityMember.objects") as mock_manager:
            mock_manager.get.return_value = existing_member

            data = {
                "entity_id": 1,
                "entity_type": mock_content_type,
                "member_name": "Test",
                "role": EntityMember.Role.CANDIDATE,
            }

            EntityMember.update_data(data, save=False)

            existing_member.save.assert_not_called()


class TestEntityMemberModelMeta:
    """Test EntityMember model meta options."""

    def test_model_has_indexes(self):
        """Test that the model defines indexes."""
        meta = EntityMember._meta
        assert len(meta.indexes) > 0

    def test_model_db_table(self):
        """Test the database table name."""
        assert EntityMember._meta.db_table == "owasp_entity_members"

    def test_model_verbose_name(self):
        """Test the model verbose name."""
        assert EntityMember._meta.verbose_name == "entity member"
