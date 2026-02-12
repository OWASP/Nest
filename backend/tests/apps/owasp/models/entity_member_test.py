"""Tests for EntityMember model."""

from unittest.mock import MagicMock, PropertyMock, patch

from django.contrib.contenttypes.models import ContentType

from apps.owasp.models.entity_member import EntityMember


class TestEntityMemberModel:
    """Test cases for EntityMember model."""

    def test_role_and_member_name_attributes(self):
        """Test role and member_name attributes are set correctly."""
        entity_member = EntityMember(
            member_name="Test User",
            role=EntityMember.Role.LEADER,
        )

        assert entity_member.role == EntityMember.Role.LEADER
        assert entity_member.member_name == "Test User"
        assert entity_member.get_role_display() == "Leader"

    def test_member_role_display(self):
        """Test get_role_display returns correct role label."""
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

    def test_str_with_member(self):
        """Test __str__ uses member.login when member exists."""
        entity_member = EntityMember(
            member_name="Different Name",
            role=EntityMember.Role.LEADER,
        )

        mock_member = MagicMock()
        mock_member.login = "test_user"

        mock_entity = MagicMock()
        mock_entity.__str__ = MagicMock(return_value="Test Entity")

        with (
            patch.object(
                type(entity_member), "member", new_callable=PropertyMock, return_value=mock_member
            ),
            patch.object(
                type(entity_member), "entity", new_callable=PropertyMock, return_value=mock_entity
            ),
        ):
            result = str(entity_member)

        assert "test_user" in result
        assert "Leader" in result
        assert "Test Entity" in result

    def test_str_without_member(self):
        """Test __str__ uses member_name when member is None."""
        entity_member = EntityMember(
            member_name="John Doe",
            role=EntityMember.Role.MEMBER,
        )

        mock_entity = MagicMock()
        mock_entity.__str__ = MagicMock(return_value="Test Entity")

        with (
            patch.object(
                type(entity_member), "member", new_callable=PropertyMock, return_value=None
            ),
            patch.object(
                type(entity_member), "entity", new_callable=PropertyMock, return_value=mock_entity
            ),
        ):
            result = str(entity_member)

        assert "John Doe" in result
        assert "Member" in result
        assert "Test Entity" in result

    def test_update_data_creates_new_member(self):
        """Test update_data creates new EntityMember when it doesn't exist."""
        mock_content_type = MagicMock(spec=ContentType)
        mock_content_type._state = MagicMock()
        mock_content_type._state.db = "default"

        data = {
            "entity_id": 1,
            "entity_type": mock_content_type,
            "member_name": "New User",
            "role": EntityMember.Role.LEADER,
            "member_email": "new@example.com",
            "order": 1,
        }

        with patch("apps.owasp.models.entity_member.EntityMember.objects.get") as mock_get:
            mock_get.side_effect = EntityMember.DoesNotExist
            result = EntityMember.update_data(data, save=False)

        assert isinstance(result, EntityMember)
        assert result.entity_id == 1
        assert result.member_name == "New User"
        assert result.role == EntityMember.Role.LEADER

    def test_from_dict_sets_all_fields(self):
        """Test from_dict sets all fields correctly."""
        mock_content_type = MagicMock(spec=ContentType)
        mock_content_type._state = MagicMock()
        mock_content_type._state.db = "default"

        entity_member = EntityMember()

        data = {
            "entity_id": 42,
            "entity_type": mock_content_type,
            "member_email": "test@example.com",
            "member_name": "Test Member",
            "order": 5,
            "role": EntityMember.Role.CANDIDATE,
        }

        entity_member.from_dict(data)

        assert entity_member.entity_id == 42
        assert entity_member.entity_type == mock_content_type
        assert entity_member.member_email == "test@example.com"
        assert entity_member.member_name == "Test Member"
        assert entity_member.order == 5
        assert entity_member.role == EntityMember.Role.CANDIDATE


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
