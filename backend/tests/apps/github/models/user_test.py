from unittest.mock import Mock, patch

import pytest

from apps.github.models.user import User
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.entity_member import EntityMember
from apps.owasp.models.project import Project


class TestUserModel:
    @pytest.mark.parametrize(
        ("name", "login", "expected_str"),
        [
            ("John Doe", "john-doe", "John Doe (john-doe)"),
            ("", "jane-doe", "jane-doe"),
            (None, "ghost", "ghost"),
            ("user", "user", "user"),
        ],
    )
    def test_str_representation(self, name, login, expected_str):
        user = User(name=name, login=login)
        assert str(user) == expected_str

    def test_from_github(self):
        gh_user_mock = Mock(
            bio="Bio",
            hireable=True,
            twitter_username="twitter",
        )

        user = User()
        user.from_github(gh_user_mock)

        assert user.bio == "Bio"
        assert user.is_hireable
        assert user.twitter_username == "twitter"

    @patch("apps.github.models.user.User.objects.get")
    @patch("apps.github.models.user.User.save")
    def test_update_data(self, mock_save, mock_get):
        gh_user_mock = Mock()
        gh_user_mock.raw_data = {"node_id": "12345"}
        gh_user_mock.bio = "Bio"
        gh_user_mock.hireable = True
        gh_user_mock.twitter_username = "twitter"

        mock_user = Mock(spec=User)
        mock_user.node_id = "12345"
        mock_get.return_value = mock_user

        updated_user = User.update_data(gh_user_mock, save=True)

        mock_get.assert_called_once_with(node_id="12345")
        assert updated_user.node_id == "12345"

    @patch("apps.github.models.user.User.objects.get")
    @patch("apps.github.models.user.User.save")
    def test_update_data_user_does_not_exist(self, mock_save, mock_get):
        gh_user_mock = Mock()
        gh_user_mock.raw_data = {"node_id": "67890"}
        gh_user_mock.bio = "New Bio"
        gh_user_mock.hireable = False
        gh_user_mock.twitter_username = "new_twitter"

        mock_get.side_effect = User.DoesNotExist

        updated_user = User.update_data(gh_user_mock, save=True)

        mock_get.assert_called_once_with(node_id="67890")
        assert updated_user.node_id == "67890"

    def test_issues_property(self):
        """Test the issues property."""
        user = User(login="test-user")
        with patch.object(User, "created_issues", all=Mock(return_value=["issue1"])):
            assert user.issues == ["issue1"]

    def test_get_absolute_url(self):
        """Test the get_absolute_url method."""
        user = User(login="test-user")
        assert user.get_absolute_url() == "/members/test-user"

    def test_nest_url_property(self):
        """Test the nest_url property."""
        user = User(login="test-user")
        with patch(
            "apps.github.models.user.get_absolute_url",
            Mock(return_value="https://test.com/members/test-user"),
        ):
            assert user.nest_url == "https://test.com/members/test-user"

    @pytest.mark.parametrize(
        ("user_type", "expected_is_bot"),
        [
            ("User", False),
            ("Bot", True),
        ],
    )
    def test_from_github_scenarios(self, user_type, expected_is_bot):
        """Test from_github with different user types."""
        gh_user_mock = Mock(
            type=user_type,
            bio=None,
            hireable=None,
            twitter_username=None,
        )
        gh_user_mock.login = "test-user"
        gh_user_mock.name = "Test User"

        user = User()
        user.from_github(gh_user_mock)

        assert user.is_bot is expected_is_bot
        assert user.login == "test-user"
        assert user.name == "Test User"

    @pytest.mark.parametrize(
        ("scenario", "get_node_id_return", "update_kwargs", "expect_save"),
        [
            ("no_node_id", None, {}, False),
            ("with_kwargs", "12345", {"is_staff": True}, True),
            ("no_save", "12345", {"save": False}, False),
        ],
    )
    @patch("apps.github.models.user.User.get_node_id")
    @patch("apps.github.models.user.User.objects.get")
    @patch("apps.github.models.user.User.save")
    def test_update_data_scenarios(
        self,
        mock_save,
        mock_get,
        mock_get_node_id,
        scenario,
        get_node_id_return,
        update_kwargs,
        expect_save,
    ):
        """Test various scenarios for the update_data method."""
        gh_user_mock = Mock()
        mock_get_node_id.return_value = get_node_id_return
        mock_user_instance = Mock(spec=User)
        mock_user_instance.save = mock_save
        mock_get.return_value = mock_user_instance

        result = User.update_data(gh_user_mock, **update_kwargs)

        if scenario == "no_node_id":
            assert result is None
            mock_save.assert_not_called()
        else:
            if "is_staff" in update_kwargs:
                assert result.is_staff is True
            if expect_save:
                mock_save.assert_called_once()
            else:
                mock_save.assert_not_called()

    @pytest.mark.parametrize(
        ("entity_model", "entity_path", "property_name"),
        [
            (Chapter, "apps.owasp.models.chapter.Chapter", "chapters"),
            (Project, "apps.owasp.models.project.Project", "projects"),
        ],
    )
    @patch("apps.github.models.user.ContentType.objects.get_for_model")
    def test_led_entities_properties(
        self, mock_get_for_model, entity_model, entity_path, property_name
    ):
        """Test the chapters and projects properties in a DRY way."""
        user = User()
        entity_ids = [1, 2]
        expected_entities = f"mocked_{property_name}"

        with (
            patch(f"{entity_path}.objects.filter") as mock_entity_filter,
            patch("apps.owasp.models.entity_member.EntityMember.objects.filter") as mock_em_filter,
        ):
            mock_queryset = Mock()
            mock_queryset.order_by.return_value = expected_entities
            mock_entity_filter.return_value = mock_queryset
            mock_em_filter.return_value.values_list.return_value = entity_ids

            result = getattr(user, property_name)

            assert result == expected_entities
            mock_get_for_model.assert_called_with(entity_model)
            mock_em_filter.assert_called_once_with(
                member=user,
                entity_type=mock_get_for_model.return_value,
                role=EntityMember.Role.LEADER,
                is_active=True,
                is_reviewed=True,
            )
            mock_entity_filter.assert_called_once_with(id__in=entity_ids, is_active=True)
            mock_queryset.order_by.assert_called_once_with("name")

    @patch("apps.github.models.user.BulkSaveModel.bulk_save")
    def test_bulk_save(self, mock_bulk_save):
        """Test the bulk_save method."""
        users = [Mock(spec=User), Mock(spec=User)]
        fields = ["name", "login"]
        User.bulk_save(users, fields=fields)
        mock_bulk_save.assert_called_once_with(User, users, fields=fields)

    @patch("apps.github.models.user.Organization.get_logins")
    def test_get_non_indexable_logins(self, mock_get_logins):
        """Test the get_non_indexable_logins method."""
        mock_get_logins.return_value = {"org1", "org2"}
        expected_logins = {
            "actions-user",
            "ghost",
            "OWASPFoundation",
            "org1",
            "org2",
        }
        assert User.get_non_indexable_logins() == expected_logins

    def test_contribution_data_default(self):
        """Test that contribution_data defaults to empty dict."""
        user = User(login="testuser", node_id="U_test123")
        assert user.contribution_data == {}

    def test_contribution_data_storage(self):
        """Test that contribution_data can store and retrieve JSON data."""
        user = User(
            login="testuser",
            node_id="U_test123",
            contribution_data={
                "2025-01-01": 5,
                "2025-01-02": 3,
                "2025-01-03": 0,
            },
        )
        assert user.contribution_data["2025-01-01"] == 5
        assert user.contribution_data["2025-01-02"] == 3
        assert user.contribution_data["2025-01-03"] == 0

    def test_contribution_data_update(self):
        """Test updating contribution_data field."""
        user = User(login="testuser", node_id="U_test123")
        user.contribution_data = {"2025-01-01": 10}
        assert user.contribution_data == {"2025-01-01": 10}

        # Update with new data
        user.contribution_data = {"2025-01-01": 15, "2025-01-02": 5}
        assert user.contribution_data["2025-01-01"] == 15
        assert user.contribution_data["2025-01-02"] == 5

    def test_releases_property(self):
        """Test the releases property."""
        user = User(login="test-user")
        with patch.object(
            User, "created_releases", all=Mock(return_value=["release1", "release2"])
        ):
            assert user.releases == ["release1", "release2"]
