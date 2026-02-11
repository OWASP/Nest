from unittest.mock import MagicMock, patch

from apps.slack.models.member import Member
from apps.slack.models.workspace import Workspace


class TestMemberModel:
    """Tests for the Member model."""

    def test_str_method(self):
        workspace = Workspace()
        member = Member(username="testuser", slack_user_id="U123", workspace=workspace)
        assert str(member) == "testuser (U123)"

        unnamed_member = Member(slack_user_id="U456", workspace=workspace)
        assert str(unnamed_member) == "Unnamed (U456)"

    def test_from_slack_method(self):
        member = Member()
        workspace = Workspace()
        slack_data = {
            "id": "U123ABC",
            "name": "testuser",
            "real_name": "Test User",
            "is_bot": False,
            "profile": {"email": "test@example.com"},
        }

        member.from_slack(slack_data, workspace)

        assert member.slack_user_id == "U123ABC"
        assert member.username == "testuser"
        assert member.workspace == workspace

    def test_update_data_creates_new_member(self):
        slack_data = {"id": "U123NEW", "name": "newuser", "is_bot": False}
        workspace = Workspace()

        with (
            patch.object(Member, "save") as mock_save,
            patch.object(Member.objects, "get", side_effect=Member.DoesNotExist) as mock_get,
        ):
            member = Member.update_data(slack_data, workspace, save=True)

        mock_get.assert_called_once_with(slack_user_id="U123NEW")
        mock_save.assert_called_once()
        assert member.username == "newuser"

    def test_update_data_updates_existing_member(self):
        updated_data = {"id": "U123EXISTING", "name": "newname", "is_bot": False}
        workspace = Workspace()
        mock_existing_member = MagicMock()

        with patch.object(Member.objects, "get", return_value=mock_existing_member) as mock_get:
            Member.update_data(updated_data, workspace, save=True)

        mock_get.assert_called_once_with(slack_user_id="U123EXISTING")
        mock_existing_member.from_slack.assert_called_once_with(updated_data, workspace)
        mock_existing_member.save.assert_called_once()

    def test_bulk_save(self):
        """Test bulk_save calls BulkSaveModel.bulk_save."""
        mock_members = [MagicMock(), MagicMock()]
        
        with patch("apps.common.models.BulkSaveModel.bulk_save") as mock_bulk_save:
            Member.bulk_save(mock_members, fields=["username"])
        
        mock_bulk_save.assert_called_once_with(Member, mock_members, fields=["username"])

    def test_update_data_no_save(self):
        """Test update_data with save=False doesn't call save."""
        slack_data = {"id": "U123NOSAVE", "name": "nosaveuser", "is_bot": False}
        workspace = Workspace()

        with (
            patch.object(Member, "save") as mock_save,
            patch.object(Member.objects, "get", side_effect=Member.DoesNotExist),
        ):
            member = Member.update_data(slack_data, workspace, save=False)

        mock_save.assert_not_called()
        assert member.username == "nosaveuser"
